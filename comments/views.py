from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from tickets.views import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .serializers import CommentSerializer
# from tickets.serializers import TicketSerializer

from .exceptions import TicketNotInProcessException
from .forms import CommentCreateForm, CommentUpdateForm
from .models import Comment
from tickets.models import Ticket


""" DJANGO VIEWS """


class CommentsListView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'comments_list_view.html'
    context_object_name = 'comments'

    def get_queryset(self):
        ticket_id = self.kwargs['pk']
        ticket = Ticket.objects.get(pk=ticket_id)
        return Comment.objects.filter(ticket=ticket).order_by('-created_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ticket'] = Ticket.objects.get(pk=self.kwargs['pk'])
        return context

    def dispatch(self, request, *args, **kwargs):
        ticket = Ticket.objects.get(pk=self.kwargs['pk'])

        if not request.user.is_superuser:
            if ticket.ticket_user != request.user:
                url = reverse('main_view')
                return HttpResponseRedirect(url)

        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentCreateForm
    template_name = 'comment_create_view.html'

    def form_valid(self, form):
        user = self.request.user
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])

        if ticket.status == 'InProcess':
            if user.is_superuser or user == ticket.ticket_user:
                comment = form.save(commit=False)
                comment.comment_user = user
                comment.ticket = ticket
                comment.text = form.cleaned_data['text']
                comment.save()

                return super().form_valid(form)
            else:
                url = reverse('main_view')
                return HttpResponseRedirect(url)
        else:
            raise TicketNotInProcessException("You cannot add comments to request that is not in 'InProcess' status.")

    def get_success_url(self):
        # ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        return reverse('comments_list_view', kwargs={'pk': self.object.ticket.pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'comment_update_view.html'
    form_class = CommentUpdateForm

    def get_object(self, queryset=None):
        comment = super().get_object()
        if comment.comment_user == self.request.user:
            return comment
        else:
            url = reverse('main_view')
            return HttpResponseRedirect(url)

    def get_success_url(self):
        return reverse_lazy('comments_list_view', kwargs={'pk': self.object.ticket.pk})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'comment_delete_view.html'

    def get_object(self, queryset=None):
        comment = super().get_object()
        if comment.comment_user == self.request.user:
            return comment
        else:
            url = reverse('main_view')
            return HttpResponseRedirect(url)

    def get_success_url(self):
        return reverse_lazy('comments_list_view', kwargs={'pk': self.object.ticket.pk})


""" DJANGO REST VIEWS """


class CommentsListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        ticket_id = kwargs.get('pk')
        ticket = Ticket.objects.get(pk=ticket_id)

        if not request.user.is_staff and ticket.ticket_user != request.user:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        comments = Comment.objects.filter(ticket=ticket).order_by('-created_date')
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)


class CommentCreateViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

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
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CommentUpdateViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        comment = super().get_object()
        if comment.comment_user == self.request.user:
            return comment
        else:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)


class CommentDeleteViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        comment = super().get_object()
        if comment.comment_user == self.request.user:
            return comment
        else:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
