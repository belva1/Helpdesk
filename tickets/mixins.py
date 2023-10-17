from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse


class LoginRequiredMixin(UserPassesTestMixin):
    """
    'test_func' ->
    method to determine the conditions under which the user has access to the view.
    If test_func returns False, then the user will be redirected to the login page defined in 'get_login_url'.
    """
    def test_func(self):
        return self.request.user.is_authenticated

    def get_login_url(self):
        return reverse('login_view')
