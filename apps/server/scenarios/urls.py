from django.urls import include, path
from rest_framework import routers

from scenarios.views import ScenarioViewSet

router = routers.SimpleRouter()

router.register(r"scenarios", ScenarioViewSet)

urlpatterns = router.urls
