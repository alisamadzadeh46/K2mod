from django import forms

from apps.accounts.models import Address


class CheckoutForm(forms.Form):
    address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        empty_label=None,
        label="آدرس ارسال",
        widget=forms.RadioSelect,
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        addresses = Address.objects.filter(user=user)
        self.fields["address"].queryset = addresses
        default = addresses.filter(is_default=True).first()
        if default and not self.is_bound:
            self.fields["address"].initial = default.pk
