""" DJANGO REST VIEWS """

from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import CommentSerializer
from .models import Comment
from tickets.models import Ticket
from .permissions import HelpdeskPermissions


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [HelpdeskPermissions]

    def list(self, request, *args, **kwargs):
        pk = kwargs.get('id')
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({'message': 'Ticket does no exist.'}, status=status.HTTP_404_NOT_FOUND)

        if (not request.user.is_staff) and request.user != ticket.ticket_user:
            return Response({'message': 'You cannot check comments for this ticket.'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('id')
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({'message': 'Ticket does no exist.'}, status=status.HTTP_404_NOT_FOUND)

        if (not request.user.is_staff) and request.user != ticket.ticket_user:
            return Response({'message': 'You cannot check comments for this ticket.'}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        pk = self.kwargs.get('id')
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({'message': 'Ticket does no exist.'}, status=status.HTTP_404_NOT_FOUND)

        queryset = ticket.comments.all()
        return queryset

    def create(self, request, *args, **kwargs):
        ticket_id = kwargs.get('id')
        ticket = Ticket.objects.get(pk=ticket_id)
        if ticket.status != 'InProcess':
            return Response({'detail': 'You cannot add comments to a request that is not in "InProcess" status.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket, comment_user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
