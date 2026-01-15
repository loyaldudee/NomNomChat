from django.urls import path
from .views import MyCommunitiesView

urlpatterns = [
    path("mine/", MyCommunitiesView.as_view()),
]
