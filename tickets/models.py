from django.utils import timezone
from django.db import models
from users.models import UM


class Ticket(models.Model):

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('InProcess', 'InProcess'),
        ('InRestoration', 'InRestoration'),

        ('DeclineToRestore', 'DeclineToRestore'),
        ('ApproveRestore', 'ApproveRestore'),

        ('Rejected', 'Rejected'),
        ('Done', 'Done'),
    ]

    ticket_user = models.ForeignKey(UM, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low')
    topic = models.CharField(max_length=64, blank=False, null=False)
    description = models.CharField(max_length=255, blank=False, null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_date = models.DateTimeField(auto_now_add=True)

    """
    When creating a request, decline_reason / reject_reason is a blank field.
    When a request is declined / rejected, it need to provide a reason in the field.
    Therefore, the field will only be required if the request is declined / rejected.
    """

    decline_reason = models.TextField(blank=True, null=False)
    reject_reason = models.TextField(blank=True, null=False)

    """
    True -> request for restoration.
    """
    restore_request = models.BooleanField(default=False)

    def __str__(self):
        return f'Topic - "{self.topic}"'


class RestorationTicketRequest(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    def __str__(self):
        return f"Restoration Request for {self.ticket.topic}."