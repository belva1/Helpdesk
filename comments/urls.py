from django.urls import path
from .views import *
from django.urls import path, include
from .views import CommentsListViewSet, CommentCreateViewSet, CommentUpdateViewSet, CommentDeleteViewSet


django_rest_urlpatterns = [
    path('rest/<str:pk>/comments/', CommentsListViewSet.as_view({'get': 'list'}), name='rest_comments_list'),
    path('rest/comment-create/<str:pk>/', CommentCreateViewSet.as_view({'post': 'create'}), name='rest_comment_create'),
    path('rest/comment-update/<str:pk>/', CommentUpdateViewSet.as_view({'put': 'update'}), name='rest_comment_update'),
    path('rest/comment-delete/<str:pk>/', CommentDeleteViewSet.as_view({'delete': 'destroy'}), name='rest_comment_delete'),
]


django_urlpatterns = [
    path('<str:pk>/', CommentsListView.as_view(), name='comments_list_view'),
    path('create-comment/<str:pk>/', CommentCreateView.as_view(), name='comment_create_view'),
    path('update-comment/<str:pk>/', CommentUpdateView.as_view(), name='comment_update_view'),
    path('delete-comment/<str:pk>/', CommentDeleteView.as_view(), name='comment_delete_view'),
]

urlpatterns = django_urlpatterns + django_rest_urlpatterns
