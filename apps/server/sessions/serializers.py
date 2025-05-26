from rest_framework import serializers


class SessionSerializer(serializers.Serializer):
    """
    Serializer for handling user login data.
    """

    email = serializers.EmailField(required=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True)
