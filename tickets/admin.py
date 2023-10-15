from django.contrib import admin
from .models import Ticket, RestorationTicketRequest

admin.site.register(Ticket)
admin.site.register(RestorationTicketRequest)