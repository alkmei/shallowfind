from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
    http_method_names = ["get", "post", "put", "delete"]

    def get_permissions(self):
        """
        Admins can perform all actions, while regular users can only view and alter their own data.
        """
        if self.request.user.is_staff:
            return [IsAuthenticated()]
        else:
            return [AllowAny()]
