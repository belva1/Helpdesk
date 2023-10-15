from django.urls import path
from .views import *
from comments.views import CommentsListView

urlpatterns = [
    path('main/', TicketsMainView.as_view(), name='main_view'),
    path('create-ticket/', TicketCreateView.as_view(), name='ticket_create_view'),
    path('ticket/<str:pk>/', TicketDetailView.as_view(), name='ticket_detail_view'),

    path('user-update-ticket/<str:pk>/', TicketUserUpdateView.as_view(), name='ticket_user_update_view'),
    path('admin-update-ticket/<str:pk>/', TicketAdminUpdateView.as_view(), name='ticket_admin_update_view'),

    path('approve-ticket/<str:pk>/', TicketApproveRestoreView.as_view(), name='ticket_approve_view'),
    path('decline-ticket/<str:pk>/', TicketDeclineToRestoreView.as_view(), name='ticket_decline_view'),
    path('restore-ticket/<str:pk>/', TicketRestoreView.as_view(), name='ticket_restore_view'),

    path('<str:pk>/', CommentsListView.as_view(), name='comments_list_view'),
]