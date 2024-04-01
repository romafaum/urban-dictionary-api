from rest_framework import serializers

class DefinitionSerializer(serializers.Serializer):
    """Serializer for defenition"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    meaning = serializers.CharField()
    example = serializers.CharField()
    author = serializers.CharField()
    date = serializers.DateField()
    likes = serializers.IntegerField()
    dislikes = serializers.IntegerField()
    links = serializers.ListField()
