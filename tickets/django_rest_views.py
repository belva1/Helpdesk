""" DJANGO REST VIEWS """

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
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
        status = self.request.query_params.get('status')  # EXMP /?status=InRestoration

        if priority:
            queryset = queryset.filter(priority=priority).distinct()

        if status:
            queryset = queryset.filter(status=status).distinct()

        return queryset

    def create(self, request, *args, **kwargs):
        request.data['ticket_user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(status='Active')
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([HelpdeskPermissions])
def ticket_decline_view(request, pk):
    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        return Response({"message": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if ticket.status != 'Active' and ticket.status != 'InRestoration':
            return Response({"message": "You cannot decline a request in this status."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if request.user.is_staff:
            if ticket.status != 'Active' and ticket.status != 'InRestoration':
                return Response({"message": "You cannot decline a request in this status."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = TicketSerializer(ticket, data=request.data, partial=True)

            if serializer.is_valid():
                if 'decline_reason' not in request.data:
                    return Response({"message": "Decline reason is required."}, status=status.HTTP_400_BAD_REQUEST)

                serializer.save(status='Declined', restore_request=False)
                return Response({"message": "Ticket declined successfully."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You don't have access to decline a request."}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([HelpdeskPermissions])
def ticket_approve_view(request, pk):
    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        return Response({"message": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if request.user.is_staff:
            if ticket.status == 'InRestoration' or ticket.status == 'Active':
                ticket.status = 'Approved'
                ticket.restore_request = False
                ticket.save()
                serializer = TicketSerializer(ticket)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "You cannot approve a request in this status."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You don't have access to approve a request."}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([HelpdeskPermissions])
def ticket_restore_view(request, pk):
    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        return Response({"message": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if request.user == ticket.ticket_user:
            if ticket.status == 'Declined':
                ticket.status = 'InRestoration'
                ticket.restore_request = True
                ticket.save()
                serializer = TicketSerializer(ticket)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "You cannot restore a request in this status."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You don't have access to restore a request."},
                            status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([HelpdeskPermissions])
def ticket_in_process_view(request, pk):
    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        return Response({"message": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if request.user.is_staff:
            if ticket.status == 'Approved':
                ticket.status = 'InProcess'
                ticket.save()
                serializer = TicketSerializer(ticket)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "You cannot move to InProcess a request in this status."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You don't have access to move to InProcess a request."},
                            status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([HelpdeskPermissions])
def ticket_done_view(request, pk):
    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        return Response({"message": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if request.user.is_staff:
            if ticket.status == 'InProcess':
                ticket.status = 'Done'
                ticket.save()
                serializer = TicketSerializer(ticket)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "You cannot move to Done a request in this status."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You don't have access to move to Done a request."},
                            status=status.HTTP_403_FORBIDDEN)
