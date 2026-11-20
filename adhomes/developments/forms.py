import time

from django import forms
from django.core import signing

from .models import Lead

# Submissions faster than this after the form was rendered are treated as bots.
MIN_SUBMIT_SECONDS = 3
_TS_SALT = "developments.leadform.ts"


class LeadForm(forms.ModelForm):
    """Public contact / viewing-request form -> saves a Lead.

    Rendered on every page (see context_processors.lead_form) and posted to
    the lead_create view. `project` / `property` arrive as hidden fields so the
    email says which development or unit the visitor was looking at.

    Spam protection (both invisible to real visitors):
    - `website` is a honeypot: hidden off-screen, so only bots fill it in.
    - `ts` is a signed render timestamp: instant submissions are bots.
    """

    website = forms.CharField(required=False)
    ts = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Lead
        fields = [
            "name", "email", "phone", "message",
            "preferred_date", "project", "property",
        ]
        widgets = {
            "name": forms.TextInput(),
            "email": forms.EmailInput(),
            "phone": forms.TextInput(attrs={"type": "tel"}),
            "message": forms.Textarea(attrs={"rows": 3}),
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "project": forms.HiddenInput(),
            "property": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Email + name are required by the model; the rest is optional.
        self.fields["message"].required = False
        self.fields["phone"].required = False
        self.fields["website"].widget.attrs.update(
            {"tabindex": "-1", "autocomplete": "off"},
        )
        if not self.is_bound:
            self.initial["ts"] = signing.TimestampSigner(salt=_TS_SALT).sign(
                str(int(time.time())),
            )

    def is_spam(self):
        """True if the honeypot was filled or the form came back too fast.

        Call after is_valid(). A missing or tampered timestamp counts as spam:
        every real form carries one from the server-side render.
        """
        if self.cleaned_data.get("website"):
            return True
        try:
            rendered = int(
                signing.TimestampSigner(salt=_TS_SALT).unsign(
                    self.cleaned_data.get("ts") or "",
                ),
            )
        except (signing.BadSignature, ValueError):
            return True
        return time.time() - rendered < MIN_SUBMIT_SECONDS

    def clean(self):
        cleaned = super().clean()
        # A viewing request for a unit also belongs to that unit's project.
        prop = cleaned.get("property")
        if prop and not cleaned.get("project"):
            cleaned["project"] = prop.project
        return cleaned
