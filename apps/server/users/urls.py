from django.urls import path
from .views import UserViewSet
from rest_framework import routers

routers = routers.SimpleRouter()

routers.register(r"users", UserViewSet)

urlpatterns = routers.urls
