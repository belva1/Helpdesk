from django.urls import path
from .views import *
from comments.django_views import CommentsListView

"""

из активного только в деклайн или апрув
из инресторейшн только в деклайн или апрув

из деклайнутого только в инресторейшн

из апрува только в инпроцесс

из инпроцесс только в комплитед, так как мы уже имеем логический деклайн

"""

django_urlpatterns = [
    path('main/', TicketsMainView.as_view(), name='main_view'),
    path('restore-tickets/', TicketsInRestorationListView.as_view(), name='restore_tickets_view'),
    path('ticket/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail_view'),

    path('create-ticket/', TicketCreateView.as_view(), name='ticket_create_view'),
    path('user-update-ticket/<int:pk>/', TicketUserUpdateView.as_view(), name='ticket_user_update_view'),

    path('restore-ticket/<int:pk>/', TicketRestoreView.as_view(), name='ticket_restore_view'),
    path('approve-ticket/<int:pk>/', TicketApproveView.as_view(), name='ticket_approve_view'),
    path('decline-ticket/<int:pk>/', TicketDeclineView.as_view(), name='ticket_decline_view'),
    path('in-process-ticket/<int:pk>/', TicketInProcessView.as_view(), name='ticket_in_process_view'),
    path('done-ticket/<int:pk>/', TicketDoneView.as_view(), name='ticket_done_view'),

    # # path('admin-update-ticket/<str:pk>/', TicketAdminUpdateView.as_view(), name='ticket_admin_update_view'),
    # path('admin-delete-ticket/<str:pk>/', TicketAdminDeleteView.as_view(), name='ticket_admin_delete_view'),
    #


    # path('<str:pk>/', CommentsListView.as_view(), name='comments_list_view'),
]

django_rest_urlpatterns = [

]

urlpatterns = django_urlpatterns + django_rest_urlpatterns
