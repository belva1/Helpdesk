from django.urls import path, include
from .django_views import *
from .django_rest_views import CommentsViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register('rest', CommentsViewSet)


django_rest_urlpatterns = [
    path('<int:id>/', include(router.urls))
]

django_urlpatterns = [
    path('<int:pk>/', CommentsListView.as_view(), name='comments_list_view'),
    path('create-comment/<int:pk>/', CommentCreateView.as_view(), name='comment_create_view'),
    path('update-comment/<int:pk>/', CommentUpdateView.as_view(), name='comment_update_view'),
    path('delete-comment/<int:pk>/', CommentDeleteView.as_view(), name='comment_delete_view'),
]

urlpatterns = django_rest_urlpatterns + django_urlpatterns
