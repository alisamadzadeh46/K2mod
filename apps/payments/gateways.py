from abc import ABC, abstractmethod

from .models import Payment


class PaymentGateway(ABC):
    name = "base"

    @abstractmethod
    def start_payment(self, order):
        """Create the payment and return the redirect url."""

    @abstractmethod
    def verify_payment(self, payment, request):
        """Check the callback and update the payment status."""


class ManualPendingGateway(PaymentGateway):
    """Marks the order as pending, no online payment."""

    name = "manual"

    def start_payment(self, order):
        from django.urls import reverse

        payment, _ = Payment.objects.get_or_create(
            order=order, defaults={"gateway": self.name, "amount": order.total_price}
        )
        return reverse("orders:confirmation", kwargs={"pk": order.pk})

    def verify_payment(self, payment, request):
        return payment.status == Payment.Status.PENDING
