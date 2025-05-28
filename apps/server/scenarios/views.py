from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from scenarios.models import Scenario
from scenarios.serializers import ScenarioSerializer


class ScenarioListCreateView(generics.ListCreateAPIView):
    """List and create scenarios"""

    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        """Filter by user if authenticated"""
        if self.request.user.is_authenticated:
            return Scenario.objects.filter(user=self.request.user)
        return Scenario.objects.none()

    def perform_create(self, serializer):
        """Set user when creating scenario"""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class ScenarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete scenario"""

    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
