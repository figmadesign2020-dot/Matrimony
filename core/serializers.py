from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)
