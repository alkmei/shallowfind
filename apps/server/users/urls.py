from django.urls import path
from .views import UserViewSet

urlpatterns = [
    path(
        "",
        UserViewSet.as_view({"get": "list", "post": "create"}),
        name="user-list",
    ),
    path(
        "<int:pk>/",
        UserViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
                "patch": "partial_update",
            }
        ),
        name="user-detail",
    ),
]
