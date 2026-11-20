from .forms import LeadForm


def lead_form(request):
    """A blank LeadForm on every page, so the request popup renders anywhere.

    auto_id=False because the form can appear twice on one page (popup + page
    form), which would otherwise produce duplicate HTML ids.
    """
    return {"lead_form": LeadForm(auto_id=False)}
