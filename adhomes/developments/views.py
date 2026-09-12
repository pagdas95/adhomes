from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .forms import LeadForm
from .models import Project, Property


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

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Thank you — your message has been sent. We'll be in touch shortly.",
        )
        return super().form_valid(form)