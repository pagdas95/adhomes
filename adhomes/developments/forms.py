from django import forms

from .models import Lead


class LeadForm(forms.ModelForm):
    """Public contact / viewing-request form -> saves a Lead."""

    class Meta:
        model = Lead
        fields = ["name", "email", "phone", "message"]
        widgets = {
            "name": forms.TextInput(),
            "email": forms.EmailInput(),
            "phone": forms.TextInput(),
            "message": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Contact page: require a message; email + name always required by model.
        self.fields["message"].required = True
        self.fields["phone"].required = False
