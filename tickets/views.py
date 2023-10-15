from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Ticket, RestorationTicketRequest
from .forms import TicketCreateForm, TicketUserUpdateForm, TicketAdminUpdateForm
from .exceptions import TicketNotActiveException


""" DJANGO VIEWS """


class LoginRequiredMixin(UserPassesTestMixin):
    """
    'test_func' ->
    method to determine the conditions under which the user has access to the view.
    If test_func returns False, then the user will be redirected to the login page defined in 'get_login_url'.
    """
    def test_func(self):
        return self.request.user.is_authenticated

    def get_login_url(self):
        return reverse('login_view')


class TicketsMainView(LoginRequiredMixin, ListView):
    template_name = 'index.html'
    """
    context_object_name ->
    this attribute specifies the name of the variable in which the object
    (or list of objects) will be available in the template context.
    """
    context_object_name = 'tickets'

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Ticket.objects.all()
        else:
            queryset = Ticket.objects.filter(ticket_user=self.request.user)
        return queryset


class TicketsToRestoreListView(LoginRequiredMixin, ListView):
    model = RestorationTicketRequest
    template_name = 'restore_tickets_view.html'
    context_object_name = 'tickets_to_restore'

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = RestorationTicketRequest.objects.all()
        else:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        return queryset


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'ticket_detail_view.html'
    context_object_name = 'ticket'

    # 'get_object' ->
    # used to retrieve an object from a database.
    def get_object(self, queryset=None):
        # self.kwargs is a dictionary that contains the arguments passed to the URL.
        ticket_id = self.kwargs.get('pk')
        try:
            ticket = self.model.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

        return ticket

    # 'get' ->
    # processes an HTTP GET request and returns an HTTP response.
    def get(self, request, *args, **kwargs):
        ticket = self.get_object()
        if not request.user.is_staff and request.user != ticket.ticket_user:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        """
        super().get(request, *args, **kwargs) ->
        calls the 'get' method of the DetailView class, passing it the request,
        *args and **kwargs arguments that were passed in the my 'get' method.
        """
        return super().get(request, *args, **kwargs)


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    template_name = 'ticket_create_view.html'
    form_class = TicketCreateForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # An instance of the 'TicketCreateForm' form is created using the data
        # submitted by the user in the POST request.
        form = TicketCreateForm(request.POST)

        if form.is_valid():
            # A 'request.user' object representing the currently authenticated user is passed as an argument.
            new_ticket = form.create_ticket(request.user)
            url = reverse('ticket_detail_view', kwargs={'pk': new_ticket.pk})
            return HttpResponseRedirect(url)
        return render(request, self.template_name, {'form': form})


class TicketUserUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    template_name = 'ticket_user_update_view.html'
    form_class = TicketUserUpdateForm

    def get_object(self, queryset=None):
        ticket_id = self.kwargs.get('pk')
        try:
            ticket = self.model.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

        return ticket

    # 'dispatch' ->
    # 1. Request pre-processing (e.g. security checks, authorization).
    # 2.Determining which HTTP method will be called (dispatch must decide which HTTP method (e.g. get, post)
    # will be called to process the request further. This decision may depend on the type of request, the request data).
    # 3. Call the appropriate HTTP method (calls a specific method, passing it all the necessary parameters).

    def dispatch(self, request, *args, **kwargs):
        ticket = self.get_object()
        if request.user == ticket.ticket_user:
            if ticket.status != 'Active':
                raise TicketNotActiveException('You cannot edit a ticket not in Active status.')
        else:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('ticket_detail_view', kwargs={'pk': self.object.pk})


class TicketAdminUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    template_name = 'ticket_admin_update_view.html'
    form_class = TicketAdminUpdateForm

    def get_object(self, queryset=None):
        ticket_id = self.kwargs.get('pk')
        try:
            ticket = self.model.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

        return ticket

    def dispatch(self, request, *args, **kwargs):
        ticket = self.get_object()
        if request.user.is_staff:
            if ticket.status == 'DeclineToRestore' or ticket.status == 'Rejected' or ticket.status == 'Done':
                url = reverse('main_view')
                return HttpResponseRedirect(url)
        else:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        current_status = form.cleaned_data['status']

        ticket = self.get_object()
        current_ticket_status = ticket.status

        if current_status == current_ticket_status:
            form.add_error('status', 'Cannot set the same status as the current status.')
            return self.form_invalid(form)

        if current_ticket_status == 'InRestoration' and current_status not in ['ApproveRestore', 'DeclineToRestore']:
            form.add_error('status', 'Can only set "ApproveRestore" or "DeclineToRestore" for a ticket in "InRestoration" status.')
            return self.form_invalid(form)

        if current_status != 'InRestoration':
            form.instance.restore_request = False

        print(f"restore_request value: {form.instance.restore_request}")

        # If the current form status is "ApproveRestore", set the status to "Active"
        # only if the current ticket status is "InRestoration".
        if current_status == 'ApproveRestore' and current_ticket_status == 'InRestoration':
            form.instance.status = 'Active'

        self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('ticket_detail_view', kwargs={'pk': self.object.pk})


# RESTORE, APPROVE, DECLINE
class TicketRestoreView(LoginRequiredMixin, View):
    model = Ticket

    def get_object(self):
        ticket_id = self.kwargs.get('pk')
        try:
            ticket = self.model.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

        return ticket

    def get(self, request, pk):
        ticket = self.get_object()
        if request.user == ticket.ticket_user:
            if ticket.status != 'DeclineToRestore':
                raise PermissionDenied('You cannot restore orders not in the “DeclineToRestore” status.')
        else:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        return render(request, 'ticket_detail_view.html', {'pk': ticket.pk})

    def post(self, request, pk):
        ticket = self.get_object()
        if ticket.status == 'DeclineToRestore':
            RestorationTicketRequest.objects.create(ticket=ticket)
            ticket.status = 'InRestoration'
            ticket.restore_request = True
            ticket.save()

        return HttpResponseRedirect(reverse('ticket_detail_view', args=[pk]))


class TicketApproveRestoreView(LoginRequiredMixin, View):
    model = Ticket
    template_name = 'ticket_admin_update_view.html'

    def get(self, request, **kwargs):
        ticket_id = self.kwargs.get('pk')
        try:
            ticket = self.model.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

        initial_data = {
            'status': 'ApproveRestore',
        }

        form = TicketAdminUpdateForm(instance=ticket, initial=initial_data)
        context = {
            'form': form,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

        form = TicketAdminUpdateForm(request.POST, instance=ticket)

        if form.is_valid():
            if form.cleaned_data['status'] == 'ApproveRestore':
                form.instance.status = 'Active'
                form.instance.restore_request = False
            form.save()
            return redirect('ticket_detail_view', pk=ticket.pk)

        context = {
            'form': form,
        }
        return render(request, self.template_name, context)


class TicketDeclineToRestoreView(LoginRequiredMixin, View):
    model = Ticket
    template_name = 'ticket_admin_update_view.html'

    def get(self, request, **kwargs):
        ticket_id = self.kwargs.get('pk')
        try:
            ticket = self.model.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

        initial_data = {
            'status': 'DeclineToRestore',
        }

        form = TicketAdminUpdateForm(instance=ticket, initial=initial_data)
        context = {
            'form': form,
        }

        return render(request, self.template_name, context)

    def post(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

        form = TicketAdminUpdateForm(request.POST, instance=ticket)

        if form.is_valid():
            form.instance.restore_request = False
            form.save()
            return redirect('ticket_detail_view', pk=ticket.pk)

        context = {
            'form': form,
        }
        return render(request, self.template_name, context)


class TicketAdminDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = 'ticket_admin_delete_view.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        ticket_id = self.kwargs.get('pk')
        try:
            ticket = self.model.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

        return render(request, self.template_name)

    def get_success_url(self):
        return reverse('main_view')


""" DJANGO REST VIEWS """
