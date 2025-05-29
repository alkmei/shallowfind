from .views import UserViewSet, AdminUserViewSet
from rest_framework import routers

routers = routers.SimpleRouter()

routers.register(r"users", UserViewSet, basename="users")
routers.register(r"admin/users", AdminUserViewSet, basename="admin-users")

urlpatterns = routers.urls
