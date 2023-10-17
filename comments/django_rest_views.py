""" DJANGO REST VIEWS """

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .serializers import CommentSerializer
# from tickets.serializers import TicketSerializer
from .models import Comment
from tickets.models import Ticket


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.ticket.ticket_user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        ticket_id = kwargs.get('pk')
        ticket = Ticket.objects.get(pk=ticket_id)

        if not request.user.is_staff and ticket.ticket_user != request.user:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        comments = Comment.objects.filter(ticket=ticket).order_by('-created_date')
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        ticket_id = kwargs.get('pk')
        ticket = Ticket.objects.get(pk=ticket_id)

        if ticket.status != 'InProcess':
            return Response({'detail': 'You cannot add comments to a request that is not in "InProcess" status.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.is_staff and user != ticket.ticket_user:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket, comment_user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
