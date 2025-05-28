from rest_framework import viewsets
from .models import Scenario
from .serializers import ScenarioSerializer


class ScenarioViewSet(viewsets.ModelViewSet):
    """
    Provides list, retrieve, create, update, and destroy actions
    for Scenario instances.
    """

    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
