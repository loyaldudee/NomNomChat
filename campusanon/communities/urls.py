from django.urls import path
from .views import MyCommunitiesView, SearchCommunitiesView

urlpatterns = [
    # Changed 'mine/' to '' so it matches the frontend call
    path("", MyCommunitiesView.as_view(), name="my-communities"),
    path("search/", SearchCommunitiesView.as_view(), name="search-communities"),
]