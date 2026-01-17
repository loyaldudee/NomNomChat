from django.urls import path
from .views import MyCommunitiesView
from .views import SearchCommunitiesView


urlpatterns = [
    path("mine/", MyCommunitiesView.as_view()),
    path("search/", SearchCommunitiesView.as_view(), name="search-communities"),

]
