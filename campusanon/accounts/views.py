from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, EmailOTP
from .utils import send_email_otp, hash_email, generate_internal_username

# ✅ Import Community Models directly for strict lookup
from communities.models import Community, CommunityMembership
from posts.models import Notification


COLLEGE_DOMAIN = "@aitpune.edu.in"

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_email = request.data.get("email")
        if not raw_email:
             return Response({"error": "Email is required"}, status=400)

        email = raw_email.strip().lower()

        if not email.endswith(COLLEGE_DOMAIN):
            return Response(
                {"error": "Access restricted. Only @aitpune.edu.in emails are allowed."}, 
                status=403
            )

        try:
            send_email_otp(email)
            return Response({"message": "OTP sent successfully"})
        except Exception as e:
            print(f"Error sending OTP: {e}")
            return Response({"error": "Failed to send email"}, status=500)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 1. Get Data
        raw_email = request.data.get("email")
        otp = request.data.get("otp")
        
        # New Registration Fields
        year = request.data.get("year")
        branch = request.data.get("branch")
        division = request.data.get("division") # e.g. "A", "B", or ""/None

        if not raw_email or not otp:
            return Response({"error": "Email and OTP are required"}, status=400)

        email = raw_email.strip().lower()

        # 2. Verify OTP
        record = EmailOTP.objects.filter(email=email).first()
        if not record:
            return Response({"error": "No OTP found"}, status=400)
        if record.is_expired():
            return Response({"error": "OTP has expired"}, status=400)
        if record.attempts >= 3:
            record.delete()
            return Response({"error": "Too many failed attempts."}, status=400)
        if record.otp != otp:
            record.attempts += 1
            record.save()
            return Response({"error": "Invalid OTP"}, status=400)

        # 3. Handle User
        email_hash = hash_email(email)
        user_exists = User.objects.filter(email_hash=email_hash).exists()

        if not user_exists:
            # --- REGISTRATION FLOW (Strict & Precise) ---
            if not year or not branch:
                 return Response({"error": "Year and Branch are required for new users"}, status=400)
            
            # Map Full Names to Short Codes
            BRANCH_MAP = {
                "Computer": "COMP",
                "Information Technology": "IT",
                "E&TC": "ENTC",
                "ENTC": "ENTC",
                "Mechanical": "MECH",
                "ASGE": "ARE",
                "ARE": "ARE"
            }
            clean_branch = BRANCH_MAP.get(branch, branch)
            clean_div = division if division in ['A', 'B'] else None

            # 🛑 Lookup the EXACT community (e.g. "1st Year COMP A")
            try:
                target_community = Community.objects.get(
                    year=year,
                    branch=clean_branch,
                    division=clean_div
                )
            except Community.DoesNotExist:
                return Response(
                    {"error": f"Class {year} {clean_branch} {clean_div or ''} not found."},
                    status=400
                )

            # Create User
            user = User.objects.create(
                email_hash=email_hash,
                year=int(year),
                branch=clean_branch,
                # We don't store division on User, but that's okay because...
                # ...we are adding them to the correct community RIGHT NOW.
                internal_username=generate_internal_username()
            )

            # ✅ Add to the Specific Division
            CommunityMembership.objects.create(user=user, community=target_community)
            
            # ✅ Add to Global
            global_comm = Community.objects.filter(is_global=True).first()
            if global_comm:
                CommunityMembership.objects.get_or_create(user=user, community=global_comm)

            is_new_user = True

        else:
            # --- LOGIN FLOW (Trust existing memberships) ---
            user = User.objects.get(email_hash=email_hash)
            if user.is_banned:
                return Response({"error": "This account has been banned."}, status=403)
            
            # 💡 IMPORTANT: We REMOVED the "Auto-Join Academic" block here.
            # Since the User model doesn't store 'division', we can't reliably 
            # know if they are 'A' or 'B' during login.
            # We trust the membership we created during registration.
            
            # Ensure Global is still there (safe fallback)
            global_comm = Community.objects.filter(is_global=True).first()
            if global_comm:
                 CommunityMembership.objects.get_or_create(user=user, community=global_comm)

            is_new_user = False
        Notification.objects.filter(recipient=user).delete()
        # 4. Generate Tokens
        refresh = RefreshToken.for_user(user)
        record.delete()

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": str(user.id),
            "username": user.internal_username,
            "is_new_user": is_new_user
        })

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "user_id": str(request.user.id),
            "internal_username": request.user.internal_username,
            "year": request.user.year,
            "branch": request.user.branch
        })