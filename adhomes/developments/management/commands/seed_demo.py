"""Seed the database with realistic sample data to play with.

Usage:
    python manage.py seed_demo          # add sample data (skips if it already exists)
    python manage.py seed_demo --flush  # delete existing developments data first, then seed

This only touches the developments app's tables. It never deletes users or
anything else. Images are left blank on purpose — the templates fall back to
static theme images, so pages render fine. Add real images in the admin later.
"""

import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from adhomes.developments.models import (
    Amenity,
    Lead,
    ProgressUpdate,
    Project,
    Property,
    PropertyType,
)

PROPERTY_TYPES = [
    "Studio",
    "1 Bedroom Apartment",
    "2 Bedroom Apartment",
    "3 Bedroom Apartment",
    "Penthouse",
    "Villa",
]

AMENITIES = [
    ("Swimming Pool", "icon-building"),
    ("Covered Parking", "icon-group"),
    ("Landscaped Gardens", "icon-map"),
    ("Energy Efficient", "icon-like"),
    ("Smart Home Ready", "icon-technological"),
    ("Storage Room", "icon-badge"),
]

# name, location, status, short_description, hero?, featured?
PROJECTS = [
    (
        "Livadia Residence",
        "Livadia, Larnaca",
        Project.Status.UNDER_CONSTRUCTION,
        "A contemporary residential development in the heart of Livadia, offering modern apartments designed around comfort and everyday living.",
        True,
        True,
    ),
    (
        "Kiti Seaside Villas",
        "Kiti, Larnaca",
        Project.Status.UPCOMING,
        "Exclusive seaside villas in Kiti, combining private outdoor space with easy access to the coastline.",
        True,
        True,
    ),
    (
        "Aradippou Park Apartments",
        "Aradippou, Larnaca",
        Project.Status.COMPLETED,
        "A completed development of bright, functional apartments beside the park in Aradippou.",
        True,
        False,
    ),
    (
        "Larnaca Bay Towers",
        "Larnaca",
        Project.Status.UNDER_CONSTRUCTION,
        "Two modern towers close to Larnaca's seafront, with a mix of apartments and penthouses.",
        False,
        True,
    ),
    (
        "Oroklini Heights",
        "Oroklini, Larnaca",
        Project.Status.SOLD_OUT,
        "A sold-out hillside development with panoramic views over Oroklini and the bay.",
        False,
        False,
    ),
]

# Per project: how many units, and how their statuses are distributed.
UNIT_STATUSES = [
    Property.Status.AVAILABLE,
    Property.Status.AVAILABLE,
    Property.Status.RESERVED,
    Property.Status.SOLD,
    Property.Status.UNDER_CONSTRUCTION,
]


class Command(BaseCommand):
    help = "Seed the database with sample developments data to play with."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing developments data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing developments data…")
            Lead.objects.all().delete()
            ProgressUpdate.objects.all().delete()
            Property.objects.all().delete()
            Project.objects.all().delete()
            Amenity.objects.all().delete()
            PropertyType.objects.all().delete()

        if Project.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Projects already exist — skipping. Use --flush to reseed."
            ))
            return

        # Property types
        types = {}
        for i, name in enumerate(PROPERTY_TYPES):
            types[name] = PropertyType.objects.create(name=name, order=i)
        self.stdout.write(f"Created {len(types)} property types.")

        # Amenities
        amenities = []
        for i, (name, icon) in enumerate(AMENITIES):
            amenities.append(Amenity.objects.create(name=name, icon=icon, order=i))
        self.stdout.write(f"Created {len(amenities)} amenities.")

        # Projects + their units
        type_cycle = list(types.values())
        total_units = 0
        featured_units_left = Property.MAX_FEATURED  # respect the max-5 cap

        for p_index, (name, location, status, short, hero, featured) in enumerate(PROJECTS):
            project = Project.objects.create(
                name=name,
                location=location,
                status=status,
                short_description=short,
                description=(
                    f"{short} {name} is developed by A.D Homeshelter with a focus on "
                    "quality construction, modern architecture and long-term value. "
                    "Every unit is finished to a high standard, in a location chosen "
                    "for its access to everyday amenities across Larnaca."
                ),
                address=f"{location}, Cyprus",
                expected_completion="Q4 2026" if status == Project.Status.UNDER_CONSTRUCTION else "",
                completion_date=(
                    datetime.date(2024, 6, 1)
                    if status == Project.Status.COMPLETED
                    else None
                ),
                show_in_hero=hero,
                show_in_featured=featured,
                is_featured=featured,
                order=p_index,
                meta_title=f"{name} — Larnaca",
                meta_description=short[:160],
            )
            project.amenities.set(amenities[: 4 + (p_index % 3)])

            # Progress update for under-construction projects
            if status == Project.Status.UNDER_CONSTRUCTION:
                ProgressUpdate.objects.create(
                    project=project,
                    percentage=65,
                    title="Exterior structure completed",
                    description=(
                        "Exterior structure completed. Interior electrical and "
                        "plumbing work currently underway."
                    ),
                    date=timezone.now().date(),
                )

            # Units — 5 per project
            for u in range(5):
                ptype = type_cycle[(p_index + u) % len(type_cycle)]
                beds = min(u, 3)
                unit_status = UNIT_STATUSES[u % len(UNIT_STATUSES)]

                # Only feature a few available units on the homepage, within the cap.
                make_featured = (
                    featured_units_left > 0
                    and unit_status == Property.Status.AVAILABLE
                    and u == 0
                )
                if make_featured:
                    featured_units_left -= 1

                Property.objects.create(
                    project=project,
                    name=f"Unit {p_index + 1}0{u + 1}",
                    property_type=ptype,
                    status=unit_status,
                    bedrooms=beds,
                    bathrooms=max(1, beds),
                    internal_area=Decimal(str(75 + u * 20)),
                    covered_area=Decimal(str(85 + u * 20)),
                    balcony_area=Decimal(str(8 + u * 2)),
                    floor=["Ground", "1st", "2nd", "3rd", "Penthouse"][u],
                    price=None if u == 4 else Decimal(str(180000 + u * 45000)),
                    price_on_request=(u == 4),
                    description=(
                        f"A {ptype.name.lower()} in {name}, offering "
                        f"{beds if beds else 'open-plan'} "
                        f"{'bedrooms' if beds != 1 else 'bedroom'} and a bright, "
                        "functional layout with quality finishes throughout."
                    ),
                    is_featured=make_featured,
                    order=u,
                    meta_title=f"Unit {p_index + 1}0{u + 1} — {name}",
                    meta_description=f"{ptype.name} for sale in {location}.",
                )
                total_units += 1

            self.stdout.write(f"  · {name}: 5 units")

        self.stdout.write(f"Created {len(PROJECTS)} projects and {total_units} units.")

        # A few sample leads
        first_project = Project.objects.first()
        first_unit = Property.objects.first()
        Lead.objects.create(
            name="Maria Georgiou",
            email="maria@example.com",
            phone="+357 99 123456",
            project=first_project,
            property=first_unit,
            preferred_date=timezone.now().date() + datetime.timedelta(days=3),
            message="I'd like to arrange a viewing for this apartment.",
            status=Lead.Status.NEW,
        )
        Lead.objects.create(
            name="Andreas Christou",
            email="andreas@example.com",
            phone="+357 96 654321",
            project=first_project,
            message="Please send me the brochure and price list.",
            status=Lead.Status.CONTACTED,
        )
        self.stdout.write("Created 2 sample leads.")

        # Summary
        self.stdout.write(self.style.SUCCESS("\nDone! Summary:"))
        self.stdout.write(f"  Property types : {PropertyType.objects.count()}")
        self.stdout.write(f"  Amenities      : {Amenity.objects.count()}")
        self.stdout.write(f"  Projects       : {Project.objects.count()}")
        self.stdout.write(f"    · in hero    : {Project.objects.filter(show_in_hero=True).count()} (max {Project.MAX_HERO})")
        self.stdout.write(f"    · featured   : {Project.objects.filter(show_in_featured=True).count()} (max {Project.MAX_FEATURED})")
        self.stdout.write(f"  Properties     : {Property.objects.count()}")
        self.stdout.write(f"    · featured   : {Property.objects.filter(is_featured=True).count()} (max {Property.MAX_FEATURED})")
        self.stdout.write(f"  Leads          : {Lead.objects.count()}")
