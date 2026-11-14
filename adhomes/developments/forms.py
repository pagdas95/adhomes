from django import forms

from .models import Lead


class LeadForm(forms.ModelForm):
    """Public contact / viewing-request form -> saves a Lead.

    Used by the contact page, the home and project page forms and the popup.
    `project` / `property` arrive as hidden fields so the email says which
    development or unit the visitor was looking at.
    """

    class Meta:
        model = Lead
        fields = ["name", "email", "phone", "message", "project", "property"]
        widgets = {
            "name": forms.TextInput(),
            "email": forms.EmailInput(),
            "phone": forms.TextInput(),
            "message": forms.Textarea(attrs={"rows": 3}),
            "project": forms.HiddenInput(),
            "property": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Email + name are required by the model; phone and message are optional.
        self.fields["message"].required = False
        self.fields["phone"].required = False

    def clean(self):
        cleaned = super().clean()
        # A viewing request for a unit also belongs to that unit's project.
        prop = cleaned.get("property")
        if prop and not cleaned.get("project"):
            cleaned["project"] = prop.project
        return cleaned
