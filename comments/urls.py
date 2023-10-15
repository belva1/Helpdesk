from django.urls import path
from .views import *


urlpatterns = [
    path('<str:pk>/', CommentsListView.as_view(), name='comments_list_view'),
]
