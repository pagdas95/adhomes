from django.urls import path

from . import views

app_name = "developments"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("properties/", views.PropertyListView.as_view(), name="property_list"),
    path("properties/<slug:slug>/", views.PropertyDetailView.as_view(), name="property_detail"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]