import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .forms import LeadForm
from .models import Project, Property

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """Homepage. Feeds the three curated showcases, each capped at 5."""

    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["hero_projects"] = (
            Project.objects.filter(show_in_hero=True)
            .order_by("order", "-created")[: Project.MAX_HERO]
        )
        ctx["featured_projects"] = (
            Project.objects.filter(show_in_featured=True)
            .order_by("order", "-created")[: Project.MAX_FEATURED]
        )
        ctx["featured_properties"] = (
            Property.objects.filter(is_featured=True)
            .select_related("project", "property_type")
            .order_by("order", "name")[: Property.MAX_FEATURED]
        )
        return ctx


class PropertyListView(ListView):
    """All properties. No filtering yet (kept deliberately simple)."""

    model = Property
    template_name = "pages/property_list.html"
    context_object_name = "properties"
    paginate_by = 12

    def get_queryset(self):
        return (
            Property.objects.select_related("project", "property_type")
            .order_by("order", "name")
        )


class ProjectDetailView(DetailView):
    """A single development, with its units, gallery, progress and amenities."""

    model = Project
    template_name = "pages/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.prefetch_related(
            "images", "amenities", "progress_updates",
            "properties__property_type",
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["units"] = (
            self.object.properties.select_related("property_type")
            .order_by("order", "name")
        )
        return ctx


class ProjectListView(ListView):
    """All projects (developments). Simple grid, no filtering yet."""

    model = Project
    template_name = "pages/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        return Project.objects.order_by("order", "-created")


class PropertyDetailView(DetailView):
    """A single property/unit, with its gallery and amenities."""

    model = Property
    template_name = "pages/property_detail.html"
    context_object_name = "property"

    def get_queryset(self):
        return Property.objects.select_related(
            "project", "property_type",
        ).prefetch_related("images", "amenities")


class ContactView(FormView):
    """Contact page. Saves submissions as Leads and shows a success message."""

    template_name = "pages/contact.html"
    form_class = LeadForm
    success_url = reverse_lazy("developments:contact")

    SUCCESS_MESSAGE = "Thank you — your message has been sent. We'll be in touch shortly."

    def is_ajax(self):
        return self.request.headers.get("x-requested-with") == "XMLHttpRequest"

    def form_valid(self, form):
        lead = form.save()
        self.notify(lead)
        # Forms on other pages submit in the background and show a pop-up.
        if self.is_ajax():
            return JsonResponse({"ok": True, "message": self.SUCCESS_MESSAGE})
        messages.success(self.request, self.SUCCESS_MESSAGE)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.is_ajax():
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({"ok": False, "errors": errors}, status=400)
        return super().form_invalid(form)

    def notify(self, lead):
        """Email the lead to the company inbox. The lead is already saved,
        so a mail failure is logged rather than shown to the visitor."""
        about = ""
        if lead.property:
            about = (
                f"Property: {lead.property.name} ({lead.property.project.name})\n"
                f"Link: {self.request.build_absolute_uri(lead.property.get_absolute_url())}\n\n"
            )
            subject = f"Viewing request for {lead.property.name} from {lead.name}"
        elif lead.project:
            about = (
                f"Project: {lead.project.name}\n"
                f"Link: {self.request.build_absolute_uri(lead.project.get_absolute_url())}\n\n"
            )
            subject = f"Enquiry about {lead.project.name} from {lead.name}"
        else:
            subject = f"New contact request from {lead.name}"

        body = (
            f"{about}"
            f"Name: {lead.name}\n"
            f"Email: {lead.email}\n"
            f"Phone: {lead.phone or '-'}\n\n"
            f"Message:\n{lead.message or '-'}\n"
        )
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],
            reply_to=[lead.email],
        )
        try:
            email.send()
        except Exception:
            logger.exception("Failed to send contact email for lead %s", lead.pk)