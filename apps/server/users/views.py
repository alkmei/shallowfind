from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, AdminUserSerializer
from .permissions import IsOwner

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for regular users to manage their own accounts.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Users can only access their own account
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        """
        Create a new user account. This endpoint allows unauthenticated access for registration.
        """
        # Override permission for registration
        self.permission_classes = [permissions.AllowAny]
        self.check_permissions(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(self, request, *args, **kwargs):
        """
        Get current user's information.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Get current user's information by ID.
        """
        instance = self.get_object()
        if instance != request.user:
            return Response(
                {"detail": "You can only access your own account."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get", "put", "patch", "delete"])
    def me(self, request):
        """
        Endpoint for users to manage their own profile at /users/me/
        """
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        elif request.method in ["PUT", "PATCH"]:
            partial = request.method == "PATCH"
            serializer = self.get_serializer(
                request.user, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == "DELETE":
            request.user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """
        Update user account (PUT).
        """
        instance = self.get_object()
        if instance != request.user:
            return Response(
                {"detail": "You can only update your own account."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update user account (PATCH).
        """
        instance = self.get_object()
        if instance != request.user:
            return Response(
                {"detail": "You can only update your own account."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete user account.
        """
        instance = self.get_object()
        if instance != request.user:
            return Response(
                {"detail": "You can only delete your own account."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admin users to manage all user accounts.
    """

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        """
        Optionally filter users based on query parameters.
        """
        queryset = User.objects.all()
        is_staff = self.request.query_params.get("is_staff", None)
        is_active = self.request.query_params.get("is_active", None)

        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() == "true")

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        return queryset

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """
        Activate a user account.
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"status": "user activated"})

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user account.
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"status": "user deactivated"})

    @action(detail=True, methods=["post"])
    def make_staff(self, request, pk=None):
        """
        Grant staff privileges to a user.
        """
        user = self.get_object()
        user.is_staff = True
        user.save()
        return Response({"status": "user granted staff privileges"})

    @action(detail=True, methods=["post"])
    def remove_staff(self, request, pk=None):
        """
        Remove staff privileges from a user.
        """
        user = self.get_object()
        user.is_staff = False
        user.save()
        return Response({"status": "staff privileges removed"})
