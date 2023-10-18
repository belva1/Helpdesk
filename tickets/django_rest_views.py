""" DJANGO REST VIEWS """
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from tickets.serializers import TicketSerializer
from .models import Ticket
from .permissions import HelpdeskPermissions


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [HelpdeskPermissions]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Ticket.objects.all()
        else:
            queryset = Ticket.objects.filter(ticket_user=self.request.user)
        priority = self.request.query_params.get('priority')  # EXMP /?priority=Low
        if priority:
            queryset = queryset.filter(priority=priority).distinct()

        return queryset


