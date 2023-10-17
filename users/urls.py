from django.urls import path
from .django_views import *
from .django_rest_views import *


django_urlpatterns = [
    path('login/', LoginView.as_view(), name='login_view'),
    path('register/', RegisterView.as_view(), name='register_view'),
    path('logout/', LogoutView.as_view(), name='logout_view'),
]

django_rest_urlpatterns = [

]

urlpatterns = django_urlpatterns + django_rest_urlpatterns
