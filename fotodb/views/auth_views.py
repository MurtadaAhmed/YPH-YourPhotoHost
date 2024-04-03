
from django.contrib.auth import login
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

# Custom:
from fotodb.forms import UserRegistrationForm, UserLoginForm

from fotodb import views


class UserLoginView(LoginView):
    template_name = 'login.html'
    form_class = UserLoginForm


class UserRegistrationView(CreateView):
    """
    A view for user registration and account creation.
    """
    template_name = 'register.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        """
        Process the registration form and log in the user upon successful registration.
        Redirect the user to the home page.
        """
        user = form.save()
        login(self.request, user)
        return redirect('home')
