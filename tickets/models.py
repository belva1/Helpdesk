# from django.utils import timezone

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
        ('Declined', 'Declined'),
        ('Approved', 'Approved'),
        ('Done', 'Done'),
    ]

    ticket_user = models.ForeignKey(UM, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low')
    topic = models.CharField(max_length=18, blank=False, null=False)
    description = models.CharField(max_length=255, blank=False, null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_date = models.DateTimeField(auto_now_add=True)

    """
    When creating a request, decline_reason is a blank field.
    When a request is declined, it will need to provide a reason in the field.
    Therefore, the field will only be required if the request is declined.
    """
    decline_reason = models.TextField(max_length=255, blank=True, null=False)

    """
    True -> request for restoration.
    """
    restore_request = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.topic}"
