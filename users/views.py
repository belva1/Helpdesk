""" DJANGO VIEWS """

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from .forms import LoginViewForm, RegisterViewForm


class LoginView(View):
    template_name = 'login_view.html'

    def get(self, request):
        form = LoginViewForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginViewForm(request.POST)
        if form.is_valid():
            user = authenticate(**form.cleaned_data)
            if user is not None:
                login(request, user)
        return render(request, self.template_name, {'form': form})


class RegisterView(View):
    template_name = 'register_view.html'

    def get(self, request):
        if not request.user.is_authenticated:
            form = RegisterViewForm()
        else:
            url = 'login_view'
            return HttpResponseRedirect(reverse(url))
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterViewForm(request.POST)
        if form.is_valid():
            form.create_user()
            url = reverse('login_view')
            return HttpResponseRedirect(url)
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request):
        url = reverse('login_view')
        logout(request)
        return HttpResponseRedirect(url)
