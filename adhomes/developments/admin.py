from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Amenity,
    Lead,
    ProgressUpdate,
    Project,
    ProjectImage,
    Property,
    PropertyImage,
    PropertyType,
)


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "thumb", "alt_text", "caption", "order")
    readonly_fields = ("thumb",)

    @admin.display(description="Preview")
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;" />',
                obj.image.url,
            )
        return "—"


class ProgressUpdateInline(admin.TabularInline):
    model = ProgressUpdate
    extra = 0
    fields = ("date", "percentage", "title", "description", "image")


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ("image", "thumb", "alt_text", "caption", "order")
    readonly_fields = ("thumb",)

    @admin.display(description="Preview")
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;" />',
                obj.image.url,
            )
        return "—"


# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------
@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "location",
        "status",
        "show_in_hero",
        "show_in_featured",
        "property_count",
        "order",
    )
    list_editable = ("order",)
    list_filter = (
        "status", "show_in_hero", "show_in_featured", "is_featured", "location",
    )
    search_fields = ("name", "location", "address", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("amenities",)
    inlines = [ProgressUpdateInline, ProjectImageInline]
    readonly_fields = ("main_image_preview", "created", "updated")
    fieldsets = (
        (None, {
            "fields": (
                "name", "slug", "status", "order",
                "short_description", "description",
            ),
        }),
        ("Homepage showcase", {
            "description": (
                "Tick to feature this project on the homepage. "
                "Max 5 in each list — you'll get an error if you exceed it."
            ),
            "fields": ("show_in_hero", "show_in_featured", "is_featured"),
        }),
        ("Location", {
            "fields": (
                "location", "address", "latitude", "longitude", "map_embed_url",
            ),
        }),
        ("Timeline", {
            "fields": ("completion_date", "expected_completion"),
        }),
        ("Media", {
            "fields": (
                "main_image", "main_image_preview", "main_image_alt", "brochure",
            ),
        }),
        ("Features", {"fields": ("amenities",)}),
        ("SEO", {
            "classes": ("collapse",),
            "fields": ("meta_title", "meta_description"),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created", "updated"),
        }),
    )

    @admin.display(description="Units")
    def property_count(self, obj):
        return obj.properties.count()

    @admin.display(description="Current image")
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="max-height:180px;border-radius:6px;" />',
                obj.main_image.url,
            )
        return "No image uploaded"


# ---------------------------------------------------------------------------
# Property
# ---------------------------------------------------------------------------
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "project",
        "property_type",
        "status",
        "bedrooms",
        "price",
        "is_featured",
    )
    list_editable = ("status",)
    list_filter = ("status", "property_type", "project", "bedrooms", "is_featured")
    search_fields = ("name", "project__name", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("project",)
    filter_horizontal = ("amenities",)
    inlines = [PropertyImageInline]
    readonly_fields = ("main_image_preview", "floor_plan_preview", "created", "updated")
    fieldsets = (
        (None, {
            "fields": (
                "project", "name", "slug", "property_type",
                "status", "is_featured", "order",
            ),
        }),
        ("Details", {
            "fields": (
                "bedrooms", "bathrooms", "parking_spaces",
                "internal_area", "covered_area", "balcony_area", "floor",
            ),
        }),
        ("Price", {"fields": ("price", "price_on_request")}),
        ("Description", {"fields": ("description",)}),
        ("Media", {
            "fields": (
                "main_image", "main_image_preview", "main_image_alt",
                "floor_plan", "floor_plan_preview", "brochure",
            ),
        }),
        ("Features", {"fields": ("amenities",)}),
        ("SEO", {
            "classes": ("collapse",),
            "fields": ("meta_title", "meta_description"),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created", "updated"),
        }),
    )

    @admin.display(description="Current image")
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="max-height:180px;border-radius:6px;" />',
                obj.main_image.url,
            )
        return "No image uploaded"

    @admin.display(description="Floor plan")
    def floor_plan_preview(self, obj):
        if obj.floor_plan:
            return format_html(
                '<img src="{}" style="max-height:180px;border-radius:6px;" />',
                obj.floor_plan.url,
            )
        return "No floor plan uploaded"


# ---------------------------------------------------------------------------
# Leads
# ---------------------------------------------------------------------------
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "project", "property", "status", "created")
    list_editable = ("status",)
    list_filter = ("status", "created", "project")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("name", "email", "phone", "project", "property",
                       "preferred_date", "message", "created")
    fieldsets = (
        ("Request", {
            "fields": (
                "name", "email", "phone",
                "project", "property", "preferred_date", "message", "created",
            ),
        }),
        ("Handling", {"fields": ("status",)}),
    )

    def has_add_permission(self, request):
        # Leads come from the public site, not created by hand.
        return False