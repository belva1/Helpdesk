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

    def get_queryset(self):
        queryset = Comment.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        ticket_id = kwargs.get('pk')
        ticket = Ticket.objects.get(pk=ticket_id)
        if ticket.status != 'InProcess':
            return Response({'detail': 'You cannot add comments to a request that is not in "InProcess" status.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket, comment_user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
