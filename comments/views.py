from django.http import Http404
from django.urls import reverse_lazy
from tickets.views import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .models import Comment, Ticket
from django.contrib.auth.decorators import user_passes_test


# def is_admin_or_ticket_creator(user, pk):
#     try:
#         ticket = Ticket.objects.get(pk=pk)
#         return user.is_staff or user == ticket.ticket_user
#     except Ticket.DoesNotExist:
#         return False
#
#
# @user_passes_test(lambda user: is_admin_or_ticket_creator(user, pk), login_url='login')
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
                raise Http404("You do not have access to comments of this request.")

        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'comment_form.html'
    fields = ['text']

    def form_valid(self, form):
        form.instance.ticket = Ticket.objects.get(pk=self.kwargs['ticket_id'])
        form.instance.comment_user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.kwargs['ticket_id']})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'comment_form.html'
    fields = ['text']

    def get_object(self, queryset=None):
        comment = super().get_object()
        if comment.comment_user == self.request.user:
            return comment
        else:
            # Если комментарий не принадлежит залогиненному пользователю, вернуть 404 ошибку или другую обработку по вашему усмотрению.
            pass

    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.ticket.pk})


# Удаление комментария
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'  # Замените на шаблон, который соответствует вашим потребностям

    def get_object(self, queryset=None):
        comment = super().get_object()
        if comment.comment_user == self.request.user:
            return comment
        else:
            # Если комментарий не принадлежит залогиненному пользователю, вернуть 404 ошибку или другую обработку по вашему усмотрению.
            pass

    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.ticket.pk})
