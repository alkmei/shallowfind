from django.urls import path
from .views import UserViewSet

urlpatterns = [
    path(
        "users/",
        UserViewSet.as_view({"get": "list", "post": "create"}),
        name="user-list",
    ),
]
