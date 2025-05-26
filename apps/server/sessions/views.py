from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SessionSerializer


class SessionView(APIView):
    """
    View to handle user login and logout sessions using email.
    """

    serializer_class = SessionSerializer

    def post(self, request):
        """
        Handle user login with email.
        """
        serializer = SessionSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return Response(
                    {"message": "Login successful"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

    def delete(self, request):
        """
        Handle user logout.
        """
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
