from django.db import models
from users.models import UM
from tickets.models import Ticket


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    comment_user = models.ForeignKey(UM, on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False)
    created_date = models.DateTimeField(auto_now_add=True)  # storing the time the comment was created.

    def __str__(self):
        return f"Comment by {self.comment_user.username} on {self.ticket.topic}"