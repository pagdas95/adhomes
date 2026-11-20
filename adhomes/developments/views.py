import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

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


class ContactView(TemplateView):
    """Contact page. Its form (lead_form, from the context processor) posts
    to LeadCreateView like every other lead form on the site."""

    template_name = "pages/contact.html"


class LeadCreateView(View):
    """Single endpoint for every lead form (popup, home, project, contact).

    Saves a Lead and emails it to LEADS_NOTIFY_EMAIL. Background (fetch)
    submissions get JSON for the "thank you" toast; plain posts redirect back
    to `next` with a flash message.

    Spam handling: honeypot / too-fast submissions are dropped silently but
    look successful; more than LEADS_RATE_LIMIT posts per IP per window get a
    friendly "try again later".
    """

    http_method_names = ["post"]

    SUCCESS_MESSAGE = "Thank you — your message has been sent. We'll be in touch shortly."
    RATE_LIMIT_MESSAGE = (
        "You've sent several messages in a short time. "
        "Please try again later, or call us on +35797570036."
    )
    ERROR_MESSAGE = "Please check the form and try again."

    def post(self, request):
        if self.rate_limited():
            return self.respond(ok=False, message=self.RATE_LIMIT_MESSAGE, status=429)

        form = LeadForm(request.POST)
        if not form.is_valid():
            errors = {f: [str(e) for e in errs] for f, errs in form.errors.items()}
            return self.respond(ok=False, message=self.ERROR_MESSAGE, errors=errors, status=400)

        if form.is_spam():
            logger.info("Dropped spam lead submission from %s", client_ip(request))
            return self.respond(ok=True, message=self.SUCCESS_MESSAGE)

        lead = form.save()
        self.notify(lead)
        return self.respond(ok=True, message=self.SUCCESS_MESSAGE)

    def rate_limited(self):
        """Fixed-window counter per IP in the cache (Redis in production).
        If the cache is unavailable, let the submission through."""
        key = f"leads:rate:{client_ip(self.request)}"
        try:
            cache.add(key, 0, timeout=settings.LEADS_RATE_WINDOW)
            count = cache.incr(key)
        except Exception:
            logger.warning("Lead rate limit check failed; allowing submission", exc_info=True)
            return False
        return count is not None and count > settings.LEADS_RATE_LIMIT

    def respond(self, *, ok, message, errors=None, status=200):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            data = {"ok": ok, "message": message}
            if errors:
                data["errors"] = errors
            return JsonResponse(data, status=status)

        if ok:
            messages.success(self.request, message)
        elif errors:
            details = " ".join(e for errs in errors.values() for e in errs)
            messages.error(self.request, f"{message} {details}")
        else:
            messages.error(self.request, message)
        return redirect(self.next_url())

    def next_url(self):
        url = self.request.POST.get("next", "")
        if url_has_allowed_host_and_scheme(
            url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return url
        return reverse("developments:home")

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
            to=[settings.LEADS_NOTIFY_EMAIL],
            reply_to=[lead.email],
        )
        try:
            email.send()
        except Exception:
            logger.exception("Failed to send lead notification email for lead %s", lead.pk)


def client_ip(request):
    """Visitor IP. In production Traefik sits in front of Django and appends
    the real client address as the last X-Forwarded-For entry."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "")
