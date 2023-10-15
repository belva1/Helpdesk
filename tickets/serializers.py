from rest_framework import serializers
from .models import Ticket, RestorationTicketRequest


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class RestorationTicketRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestorationTicketRequest
        fields = '__all__'