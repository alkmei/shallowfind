from django.urls import include, path
from scenarios import views
from scenarios.views import ScenarioListCreateView

urlpatterns = [
    path(
        "",
        ScenarioListCreateView.as_view(),
        name="scenario",
    ),
]
