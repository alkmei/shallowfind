from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ScenarioViewSet

router = DefaultRouter()
router.register(r"scenarios", ScenarioViewSet, basename="scenario")

urlpatterns = [
    path("", include(router.urls)),
]
