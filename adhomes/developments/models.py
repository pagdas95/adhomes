"""Models for the property development website.

Core relationship:  Project (a development/building) -> Property (a unit).
Everything else is a small supporting model that hangs off those two.
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------
class PropertyType(models.Model):
    """Manageable property/unit type (Studio, 2 Bedroom Apartment, Villa...)."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Property type"
        verbose_name_plural = "Property types"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Amenity(models.Model):
    """Reusable feature/amenity, shared by projects and properties."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional CSS icon class (e.g. a Font Awesome class).",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Amenity"
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Project (a development / building)
# ---------------------------------------------------------------------------
class Project(models.Model):
    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        UNDER_CONSTRUCTION = "under_construction", "Under Construction"
        COMPLETED = "completed", "Completed"
        SOLD_OUT = "sold_out", "Sold Out"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.CharField(
        max_length=300,
        blank=True,
        help_text="One or two lines used on cards and listings.",
    )
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPCOMING,
        db_index=True,
    )

    # Location
    location = models.CharField(
        max_length=150,
        blank=True,
        help_text="Area / town, e.g. Livadia, Larnaca.",
    )
    address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
    )
    map_embed_url = models.URLField(
        blank=True,
        help_text="Optional Google Maps embed URL.",
    )

    # Timeline
    completion_date = models.DateField(null=True, blank=True)
    expected_completion = models.CharField(
        max_length=100,
        blank=True,
        help_text="Free text, e.g. 'Q4 2026', when an exact date is unknown.",
    )

    # Media
    main_image = models.ImageField(upload_to="projects/", blank=True)
    main_image_alt = models.CharField(max_length=200, blank=True)
    brochure = models.FileField(upload_to="projects/brochures/", blank=True)

    amenities = models.ManyToManyField(
        Amenity, related_name="projects", blank=True,
    )

    is_featured = models.BooleanField(default=False, db_index=True)

    # Homepage showcase controls (max 5 each, enforced in clean()).
    show_in_hero = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Show this project in the homepage hero slider (max 5).",
    )
    show_in_featured = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Show this project in the homepage 'Featured Projects' strip (max 5).",
    )

    order = models.PositiveIntegerField(default=0)

    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Homepage showcase caps
    MAX_HERO = 5
    MAX_FEATURED = 5

    class Meta:
        ordering = ["order", "-created"]

    def __str__(self):
        return self.name

    def clean(self):
        """Enforce the max-5 caps for the two homepage showcase slots."""
        from django.core.exceptions import ValidationError

        if self.show_in_hero:
            qs = Project.objects.filter(show_in_hero=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= self.MAX_HERO:
                raise ValidationError({
                    "show_in_hero": (
                        f"Only {self.MAX_HERO} projects can be shown in the hero "
                        f"slider. Uncheck another project first."
                    ),
                })

        if self.show_in_featured:
            qs = Project.objects.filter(show_in_featured=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= self.MAX_FEATURED:
                raise ValidationError({
                    "show_in_featured": (
                        f"Only {self.MAX_FEATURED} projects can be shown in the "
                        f"'Featured Projects' strip. Uncheck another project first."
                    ),
                })

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("developments:project_detail", kwargs={"slug": self.slug})

    @property
    def available_properties(self):
        return self.properties.filter(status=Property.Status.AVAILABLE)

    @property
    def latest_progress(self):
        return self.progress_updates.first()


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, related_name="images", on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="projects/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.project.name}"


class ProgressUpdate(models.Model):
    """A construction-progress snapshot shown to visitors. Kept deliberately simple."""

    project = models.ForeignKey(
        Project, related_name="progress_updates", on_delete=models.CASCADE,
    )
    percentage = models.PositiveIntegerField(
        default=0, help_text="Overall completion, 0-100.",
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Short status line, e.g. 'Exterior structure completed'.",
    )
    description = models.TextField(blank=True)
    date = models.DateField(help_text="Date of this update.")
    image = models.ImageField(upload_to="projects/progress/", blank=True)

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Construction progress update"
        verbose_name_plural = "Construction progress updates"

    def __str__(self):
        return f"{self.project.name} - {self.percentage}% ({self.date})"


# ---------------------------------------------------------------------------
# Property (a unit within a project)
# ---------------------------------------------------------------------------
class Property(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        RESERVED = "reserved", "Reserved"
        SOLD = "sold", "Sold"
        UNDER_CONSTRUCTION = "under_construction", "Under Construction"

    project = models.ForeignKey(
        Project, related_name="properties", on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=150,
        help_text="Unit name or number, e.g. 'Apartment 201'.",
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    property_type = models.ForeignKey(
        PropertyType,
        related_name="properties",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
    )

    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    parking_spaces = models.PositiveIntegerField(default=0)

    internal_area = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Square metres.",
    )
    covered_area = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Square metres.",
    )
    balcony_area = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Balcony / veranda, square metres.",
    )
    floor = models.CharField(
        max_length=50, blank=True,
        help_text="e.g. 'Ground', '2nd', 'Penthouse level'.",
    )

    price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    price_on_request = models.BooleanField(default=False)

    description = models.TextField(blank=True)

    main_image = models.ImageField(upload_to="properties/", blank=True)
    main_image_alt = models.CharField(max_length=200, blank=True)
    floor_plan = models.ImageField(upload_to="properties/floorplans/", blank=True)
    brochure = models.FileField(upload_to="properties/brochures/", blank=True)

    amenities = models.ManyToManyField(
        Amenity, related_name="properties", blank=True,
    )

    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Show this property in the homepage 'Choose an apartment' slider (max 5).",
    )
    order = models.PositiveIntegerField(default=0)

    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Homepage showcase cap
    MAX_FEATURED = 5

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return f"{self.name} - {self.project.name}"

    def clean(self):
        """Enforce the max-5 cap for the homepage properties slider."""
        from django.core.exceptions import ValidationError

        if self.is_featured:
            qs = Property.objects.filter(is_featured=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= self.MAX_FEATURED:
                raise ValidationError({
                    "is_featured": (
                        f"Only {self.MAX_FEATURED} properties can be featured on "
                        f"the homepage. Uncheck another property first."
                    ),
                })

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.name}-{self.project.name}"
            self.slug = _unique_slug(self, base)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("developments:property_detail", kwargs={"slug": self.slug})


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, related_name="images", on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="properties/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.property.name}"


# ---------------------------------------------------------------------------
# Leads / viewing requests
# ---------------------------------------------------------------------------
class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        COMPLETED = "completed", "Completed"

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)

    project = models.ForeignKey(
        Project,
        related_name="leads",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    property = models.ForeignKey(
        Property,
        related_name="leads",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    preferred_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Lead / viewing request"
        verbose_name_plural = "Leads / viewing requests"

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _unique_slug(instance, value):
    """Return a unique slug for `value` within the instance's model."""
    base = slugify(value)[:200] or "item"
    model = instance.__class__
    slug = base
    n = 2
    qs = model.objects.all()
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(slug=slug).exists():
        suffix = f"-{n}"
        slug = f"{base[: 200 - len(suffix)]}{suffix}"
        n += 1
    return slug