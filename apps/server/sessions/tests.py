from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class SessionTests(APITestCase):
    def setUp(self):
        """
        Set up a test user for login tests.
        """
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        self.login_url = "/api/session/"
        self.logout_url = "/api/session/"

    def test_login_success(self):
        """
        Test that a user can log in with valid credentials.
        """
        response = self.client.post(
            self.login_url,
            {"email": "testuser@example.com", "password": "testpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Login successful")

    def test_login_failure_invalid_credentials(self):
        """
        Test that login fails with invalid credentials.
        """
        response = self.client.post(
            self.login_url,
            {"email": "testuser@example.com", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Invalid credentials")

    def test_logout_success(self):
        """
        Test that a logged-in user can log out successfully.
        """
        # Log in the user first
        self.client.post(
            self.login_url,
            {"email": "testuser@example.com", "password": "testpassword"},
        )

        # Log out
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Logout successful")

    def test_logout_without_login(self):
        """
        Test that logout fails if the user is not logged in.
        """
        response = self.client.delete(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Logout successful")
