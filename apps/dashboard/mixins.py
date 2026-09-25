from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ActiveTabMixin:
    """Sets the active sidebar item."""

    active_tab = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = self.active_tab
        return context
