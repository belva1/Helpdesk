from rest_framework import serializers
from .models import UM


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UM
        fields = ('id', 'username', 'email', 'first_name', 'last_name')