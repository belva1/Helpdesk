""" DJANGO VIEWS """

from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Ticket
from .forms import TicketCreateForm, TicketUserUpdateForm, TicketDeclineForm
from .exceptions import IsNotActiveOrInRestorationTicketException, IsNotActiveTicketException, \
    IsNotDeclinedTicketException, IsNotCreatorOfTicketException, IsNotApprovedTicketException, \
    IsNotInProcessTicketException
from .mixins import LoginRequiredMixin


# MAIN, IN-RESTORATION, DETAIL VIEWS
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


class TicketsInRestorationListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'restore_tickets_view.html'
    context_object_name = 'tickets_to_restore'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Ticket.objects.filter(status='InRestoration')
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
    def get(self, *args, **kwargs):
        ticket = self.get_object()
        if not self.request.user.is_staff and self.request.user != ticket.ticket_user:
            url = reverse('main_view')
            return HttpResponseRedirect(url)
        """
        super().get(request, *args, **kwargs) ->
        calls the 'get' method of the DetailView class, passing it the request,
        *args and **kwargs arguments that were passed in the my 'get' method.
        """
        return super().get(*args, **kwargs)


# CREATE VIEW
class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    template_name = 'ticket_create_view.html'
    form_class = TicketCreateForm

    def get(self, request, **kwargs):
        if request.user.is_staff:
            raise Http404("Users with privileges cannot create requests.")
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, **kwargs):
        if request.user.is_staff:
            raise Http404("Users with privileges cannot create requests.")
        # An instance of the 'TicketCreateForm' form is created using the data
        # submitted by the user in the POST request.
        form = TicketCreateForm(request.POST)

        if form.is_valid():
            # A 'request.user' object representing the currently authenticated user is passed as an argument.
            new_ticket = form.create_ticket(request.user)
            url = reverse('ticket_detail_view', kwargs={'pk': new_ticket.pk})
            return HttpResponseRedirect(url)
        return render(request, self.template_name, {'form': form})


# UPDATE VIEW
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

    def get(self, request, *args, **kwargs):
        ticket = self.get_object()
        if request.user == ticket.ticket_user:
            if ticket.status != 'Active':
                raise IsNotActiveTicketException('You cannot edit a ticket not in Active status.')
        else:
            raise IsNotCreatorOfTicketException('You cannot restore request that you are not the creator of.')

        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('ticket_detail_view', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.initial['priority'] = self.object.priority
        form.initial['description'] = self.object.description
        return form


# DELETE VIEW
class TicketAdminDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = 'ticket_admin_delete_view.html'
    context_object_name = 'ticket'

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        ticket_id = self.kwargs.get('pk')
        try:
            ticket = self.model.objects.get(pk=ticket_id)
            return ticket
        except Ticket.DoesNotExist:
            raise Http404('The ticket you are trying to find does not exist.')

    def get_success_url(self):
        return reverse('main_view')


# RESTORE, APPROVE, DECLINE
class TicketRestoreView(LoginRequiredMixin, View):
    model = Ticket

    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if request.user != ticket.ticket_user:
            raise IsNotCreatorOfTicketException('You cannot restore request that you are not the creator of.')

        if ticket.status == 'Declined':
            ticket.status = 'InRestoration'
            ticket.restore_request = True
            ticket.save()
        else:
            raise IsNotDeclinedTicketException('You cannot restore a request in this status.')

        return HttpResponseRedirect(reverse('ticket_detail_view', args=[pk]))


class TicketDeclineView(LoginRequiredMixin, View):
    model = Ticket
    template_name = 'ticket_decline_view.html'

    @method_decorator([staff_member_required])
    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.status != 'Active' and ticket.status != 'InRestoration':
            raise IsNotActiveOrInRestorationTicketException('You cannot decline a request in this status.')

        form = TicketDeclineForm()
        return render(request, 'ticket_decline_view.html', {'form': form, 'ticket': ticket})

    @method_decorator([staff_member_required])
    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)

        form = TicketDeclineForm(request.POST)
        if form.is_valid():
            ticket.decline_reason = form.cleaned_data['decline_reason']
            ticket.status = 'Declined'
            ticket.restore_request = False
            ticket.save()

            return HttpResponseRedirect(reverse('ticket_detail_view', args=[pk]))

        return render(request, 'ticket_decline_view', {'form': form, 'ticket': ticket})


class TicketApproveView(LoginRequiredMixin, View):
    model = Ticket

    @method_decorator([staff_member_required])
    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.status == 'InRestoration' or ticket.status == 'Active':
            ticket.status = 'Approved'
            ticket.restore_request = False
            ticket.save()
        else:
            raise IsNotActiveOrInRestorationTicketException('You cannot approve a request in this status.')

        return HttpResponseRedirect(reverse('ticket_detail_view', args=[pk]))


# IN-PROCESS, DONE
class TicketInProcessView(LoginRequiredMixin, View):
    model = Ticket

    @method_decorator([staff_member_required])
    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.status == 'Approved':
            ticket.status = 'InProcess'
            ticket.save()
        else:
            raise IsNotApprovedTicketException('You cannot move to InProcess a request in this status.')

        return HttpResponseRedirect(reverse('ticket_detail_view', args=[pk]))


class TicketDoneView(LoginRequiredMixin, View):
    model = Ticket

    @method_decorator([staff_member_required])
    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.status == 'InProcess':
            ticket.status = 'Done'
            ticket.save()
        else:
            raise IsNotInProcessTicketException('You cannot move to Done a request in this status.')

        return HttpResponseRedirect(reverse('ticket_detail_view', args=[pk]))
