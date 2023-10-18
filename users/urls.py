from django.urls import path
from .views import *


urlpatterns = [
    path('login/', LoginView.as_view(), name='login_view'),
    path('register/', RegisterView.as_view(), name='register_view'),
    path('logout/', LogoutView.as_view(), name='logout_view'),
]
