from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    comment_user = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'comment_user', 'text']
