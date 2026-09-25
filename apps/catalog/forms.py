from django import forms

from .models import ProductComment


class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "نظر خود را درباره این محصول بنویسید..."}),
        }
