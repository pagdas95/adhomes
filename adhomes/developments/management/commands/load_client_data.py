"""Load the real client data (3 projects + their units), cleaned and translated.

Usage:
    python manage.py load_client_data            # add if not already present
    python manage.py load_client_data --replace  # delete these 3 projects first, then re-add

Only touches the three client projects by name; leaves demo/other data alone.
Images are left blank — add them in the admin once the client sends photos.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from adhomes.developments.models import (
    Amenity,
    ProgressUpdate,
    Project,
    Property,
    PropertyType,
)

# ---- shared amenities (cleaned from the client's Greeklish notes) ----
AMENITIES = [
    ("Swimming Pool", "icon-building"),
    ("Photovoltaic System (3kW)", "icon-technological"),
    ("Security Aluminium", "icon-badge"),
    ("Ceramic Tiles", "icon-home-automation"),
    ("Custom Kitchen", "icon-group"),
    ("Anti-seismic Construction", "icon-like"),
    ("Covered Parking", "icon-group"),
    ("Private Storage", "icon-badge"),
    ("Roof Garden", "icon-leaf"),
]

PROPERTY_TYPES = [
    "Studio", "1 Bedroom Apartment", "2 Bedroom Apartment",
    "3 Bedroom Apartment", "Penthouse", "House", "Villa",
]

# ---- Projects (cleaned + translated) ----
PROJECTS = [
    {
        "name": "Kiti Houses",
        "location": "Kiti, Larnaca",
        "address": "Ilia Venezi, Kiti, Larnaca, Cyprus",
        "status": Project.Status.SOLD_OUT,
        "short": "A completed development of four modern two-storey houses in Kiti, Larnaca.",
        "description": (
            "This project involved the construction of four two-storey houses, "
            "each approximately 148 m². Three of the houses have three bedrooms "
            "and three bathrooms, while the fourth has four bedrooms. Three houses "
            "include a private swimming pool; the fourth does not.\n\n"
            "Site works began in October 2023 and the houses were delivered in "
            "January 2025. The construction was carried out with particular "
            "attention to anti-seismic protection and durability, by professional "
            "crews across all the required trades.\n\n"
            "The houses feature a pitched roof and photovoltaic systems, with "
            "completed flooring, landscaped outdoor areas and gardens. Materials "
            "and equipment were supplied by established partners including Adelfoi "
            "Mylonas, Adelfoi Fogous, Multiklima and Yiannis Savvides."
        ),
        "completion_date": "2025-01-31",
        "expected_completion": "",
        "maps": "https://share.google/rRSo3rdvwA18q9wKt",
        "amenities": ["Swimming Pool", "Photovoltaic System (3kW)", "Security Aluminium",
                      "Ceramic Tiles", "Custom Kitchen", "Anti-seismic Construction"],
        "progress": None,
    },
    {
        "name": "Aradippou Houses",
        "location": "Aradippou, Larnaca",
        "address": "Kalavryton 8–18, 7140 Aradippou, Larnaca, Cyprus",
        "status": Project.Status.SOLD_OUT,
        "short": "A completed development of six modern two-storey houses in Aradippou, Larnaca.",
        "description": (
            "This project involved the construction of six modern two-storey "
            "houses, each approximately 164 m², designed with varied layouts. "
            "Four houses have three bedrooms and three bathrooms; the other two "
            "have four bedrooms. Two of the six houses include a swimming pool.\n\n"
            "Site works began in March 2025 and the project was completed in "
            "February 2026, when the houses were delivered. Construction included "
            "anti-seismic provisions, a pitched roof and photovoltaic systems, "
            "completed interior flooring and installations, and landscaped gardens.\n\n"
            "Materials and works were supplied and carried out by partners "
            "including Adelfoi Mylonas, Adelfoi Fogous, J.K. Plumbing and Heating "
            "Eco Ltd and Yiannis Savvides."
        ),
        "completion_date": "2026-02-28",
        "expected_completion": "",
        "maps": "https://www.google.com/maps?q=Kalavryton+Aradippou+Larnaca",
        "amenities": ["Swimming Pool", "Photovoltaic System (3kW)", "Security Aluminium",
                      "Ceramic Tiles", "Custom Kitchen", "Anti-seismic Construction"],
        "progress": None,
    },
    {
        "name": "Livadia Apartments",
        "location": "Livadia, Larnaca",
        "address": "Smyrnis 6, Livadia, Larnaca 7060, Cyprus",
        "status": Project.Status.UNDER_CONSTRUCTION,
        "short": "A modern two-storey apartment building in Livadia with just 6 apartments.",
        "description": (
            "A contemporary two-storey apartment building in the Livadia area, "
            "comprising just 6 apartments — 3 per floor — for a quieter, more "
            "private living environment.\n\n"
            "Every apartment has 2 bedrooms, its own parking space and a private "
            "storage room. The building also features a roof garden: an attractive "
            "shared space for relaxation and enjoying the view.\n\n"
            "Designed with modern architecture and aesthetics, the building follows "
            "current construction standards and includes anti-seismic protection, "
            "with an emphasis on safety and long-term durability."
        ),
        "completion_date": None,
        "expected_completion": "Q2 2026",
        "maps": "https://www.google.com/maps?q=Smyrnis+Livadia+Larnaca",
        "amenities": ["Covered Parking", "Private Storage", "Roof Garden",
                      "Anti-seismic Construction", "Security Aluminium"],
        "progress": {
            "percentage": 60,
            "title": "Construction in progress",
            "description": "Structural works advancing; interior installations underway. Expected completion Q2 2026.",
            "date": "2026-01-15",
        },
    },
]

# ---- Units (cleaned + translated). project = exact project name above. ----
UNITS = [
    # Kiti Houses (4)
    {"project": "Kiti Houses", "name": "House 21 (Ilia Venezi)", "type": "House", "status": Property.Status.SOLD,
     "beds": 4, "baths": 3, "parking": 1, "internal": 148, "plot": 221, "floor": "2",
     "outdoor": "Covered veranda 19 m², 1st-floor veranda 3 m², Entrance 13 m²",
     "desc": "A modern, fully-compliant home. At the owner's request an additional room was created by enclosing one of the verandas."},
    {"project": "Kiti Houses", "name": "House 19 (Ilia Venezi)", "type": "House", "status": Property.Status.SOLD,
     "beds": 3, "baths": 3, "parking": 1, "internal": 146, "plot": 225, "floor": "2",
     "outdoor": "Covered veranda 19 m², 1st-floor veranda 5 m², Entrance 13 m²",
     "desc": "A modern 3-bedroom home — spacious and comfortable, on a central road with easy access, and featuring a private swimming pool."},
    {"project": "Kiti Houses", "name": "House 17 (Ilia Venezi)", "type": "House", "status": Property.Status.SOLD,
     "beds": 3, "baths": 3, "parking": 1, "internal": 146, "plot": 227, "floor": "2",
     "outdoor": "Covered veranda 19 m², 1st-floor veranda 5 m², Entrance 13 m²",
     "desc": "A modern 3-bedroom home — spacious and comfortable, on a central road with easy access, and featuring a private swimming pool."},
    {"project": "Kiti Houses", "name": "House 15 (Ilia Venezi)", "type": "House", "status": Property.Status.SOLD,
     "beds": 3, "baths": 3, "parking": 1, "internal": 149, "plot": 227, "floor": "2",
     "outdoor": "Covered veranda 19 m², 1st-floor veranda 3 m², Entrance 13 m²",
     "desc": "A modern 3-bedroom home — spacious and comfortable, on a central road with easy access, and featuring a private swimming pool."},
    # Aradippou Houses (6)
    {"project": "Aradippou Houses", "name": "Kalavryton 18", "type": "Villa", "status": Property.Status.SOLD,
     "beds": 4, "baths": 3, "parking": 1, "internal": 164, "plot": 335, "floor": "2",
     "outdoor": "Covered veranda 22 m², Garden 52 m², Pool area 110 m², Entrance 19 m²",
     "desc": "A modern 4-bedroom home — spacious and comfortable, on a central road with easy access."},
    {"project": "Aradippou Houses", "name": "Kalavryton 16", "type": "Villa", "status": Property.Status.SOLD,
     "beds": 3, "baths": 3, "parking": 1, "internal": 164, "plot": 340, "floor": "2",
     "outdoor": "Covered veranda 22 m², Garden 56 m², Pool area 110 m², Entrance 19 m²",
     "desc": "A modern 3-bedroom home — spacious and comfortable, on a central road with easy access."},
    {"project": "Aradippou Houses", "name": "Kalavryton 14", "type": "Villa", "status": Property.Status.SOLD,
     "beds": 3, "baths": 3, "parking": 1, "internal": 164, "plot": 341, "floor": "2",
     "outdoor": "Covered veranda 22 m², Garden 58 m², Pool area 110 m², Entrance 19 m²",
     "desc": "A modern 3-bedroom home — spacious and comfortable, on a central road with easy access, and featuring a private swimming pool."},
    {"project": "Aradippou Houses", "name": "Kalavryton 12", "type": "Villa", "status": Property.Status.SOLD,
     "beds": 3, "baths": 3, "parking": 1, "internal": 164, "plot": 341, "floor": "2",
     "outdoor": "Covered veranda 22 m², Garden 58 m², Pool area 110 m², Entrance 19 m²",
     "desc": "A modern 3-bedroom home — spacious and comfortable, on a central road with easy access, and featuring a private swimming pool."},
    {"project": "Aradippou Houses", "name": "Kalavryton 10", "type": "Villa", "status": Property.Status.SOLD,
     "beds": 3, "baths": 3, "parking": 1, "internal": 164, "plot": 341, "floor": "2",
     "outdoor": "Covered veranda 22 m², Garden 58 m², Pool area 110 m², Entrance 19 m²",
     "desc": "A modern 3-bedroom home — spacious and comfortable, on a central road with easy access."},
    {"project": "Aradippou Houses", "name": "Kalavryton 8", "type": "Villa", "status": Property.Status.SOLD,
     "beds": 4, "baths": 3, "parking": 1, "internal": 164, "plot": 360, "floor": "2",
     "outdoor": "Covered veranda 22 m², Garden 51 m², Pool area 113 m², Entrance 23.5 m²",
     "desc": "A modern 4-bedroom home — spacious and comfortable, on a central road with easy access."},
    # Livadia Apartments (6) — prices are + 5% VAT
    {"project": "Livadia Apartments", "name": "Apartment 101", "type": "2 Bedroom Apartment", "status": Property.Status.UNDER_CONSTRUCTION,
     "beds": 2, "baths": 2, "parking": 1, "internal": 79, "plot": 99, "floor": "Ground",
     "outdoor": "Veranda 20 m²", "price": 210000,
     "desc": "A 2-bedroom apartment in a modern building in Livadia. Price excludes VAT (+5% VAT applies)."},
    {"project": "Livadia Apartments", "name": "Apartment 102", "type": "2 Bedroom Apartment", "status": Property.Status.UNDER_CONSTRUCTION,
     "beds": 2, "baths": 2, "parking": 1, "internal": 87, "plot": 100, "floor": "Ground",
     "outdoor": "Veranda 13 m²", "price": 210000,
     "desc": "A 2-bedroom apartment in a modern building in Livadia. Price excludes VAT (+5% VAT applies)."},
    {"project": "Livadia Apartments", "name": "Apartment 103", "type": "2 Bedroom Apartment", "status": Property.Status.UNDER_CONSTRUCTION,
     "beds": 2, "baths": 2, "parking": 1, "internal": 80, "plot": 92, "floor": "Ground",
     "outdoor": "Veranda 12 m²", "price": 210000,
     "desc": "A 2-bedroom apartment in a modern building in Livadia. Price excludes VAT (+5% VAT applies)."},
    {"project": "Livadia Apartments", "name": "Apartment 201", "type": "2 Bedroom Apartment", "status": Property.Status.UNDER_CONSTRUCTION,
     "beds": 2, "baths": 2, "parking": 1, "internal": 79, "plot": 99, "floor": "1st",
     "outdoor": "Veranda 20 m²", "price": 250000,
     "desc": "A 2-bedroom apartment in a modern building in Livadia. Price excludes VAT (+5% VAT applies)."},
    {"project": "Livadia Apartments", "name": "Apartment 202", "type": "2 Bedroom Apartment", "status": Property.Status.UNDER_CONSTRUCTION,
     "beds": 2, "baths": 2, "parking": 1, "internal": 87, "plot": 100, "floor": "1st",
     "outdoor": "Veranda 13 m²", "price": 250000,
     "desc": "A 2-bedroom apartment in a modern building in Livadia. Price excludes VAT (+5% VAT applies)."},
    {"project": "Livadia Apartments", "name": "Apartment 203", "type": "2 Bedroom Apartment", "status": Property.Status.UNDER_CONSTRUCTION,
     "beds": 2, "baths": 2, "parking": 1, "internal": 80, "plot": 92, "floor": "1st",
     "outdoor": "Veranda 12 m²", "price": 250000,
     "desc": "A 2-bedroom apartment in a modern building in Livadia. Price excludes VAT (+5% VAT applies)."},
]


class Command(BaseCommand):
    help = "Load the cleaned, translated real client data (3 projects + units)."

    def add_arguments(self, parser):
        parser.add_argument("--replace", action="store_true",
                            help="Delete these 3 projects first, then re-add.")

    @transaction.atomic
    def handle(self, *args, **options):
        names = [p["name"] for p in PROJECTS]

        if options["replace"]:
            Project.objects.filter(name__in=names).delete()
            self.stdout.write("Removed existing client projects.")

        # lookups
        types = {t: PropertyType.objects.get_or_create(
            name=t, defaults={"order": i})[0] for i, t in enumerate(PROPERTY_TYPES)}
        amen = {a: Amenity.objects.get_or_create(
            name=a, defaults={"icon": icon, "order": i})[0]
            for i, (a, icon) in enumerate(AMENITIES)}

        created_p = created_u = 0
        for pdata in PROJECTS:
            if Project.objects.filter(name=pdata["name"]).exists():
                self.stdout.write(self.style.WARNING(
                    f"Skipping '{pdata['name']}' (already exists). Use --replace to overwrite."))
                continue
            proj = Project.objects.create(
                name=pdata["name"],
                location=pdata["location"],
                address=pdata["address"],
                status=pdata["status"],
                short_description=pdata["short"],
                description=pdata["description"],
                completion_date=pdata["completion_date"] or None,
                expected_completion=pdata["expected_completion"],
                map_embed_url=pdata["maps"],
            )
            proj.amenities.set([amen[a] for a in pdata["amenities"] if a in amen])
            if pdata["progress"]:
                ProgressUpdate.objects.create(project=proj, **pdata["progress"])
            created_p += 1

            for u in [x for x in UNITS if x["project"] == pdata["name"]]:
                Property.objects.create(
                    project=proj,
                    name=u["name"],
                    property_type=types.get(u["type"]),
                    status=u["status"],
                    bedrooms=u["beds"],
                    bathrooms=u["baths"],
                    parking_spaces=u["parking"],
                    internal_area=Decimal(str(u["internal"])),
                    covered_area=Decimal(str(u["plot"])),
                    outdoor_areas=u.get("outdoor", ""),
                    floor=u["floor"],
                    price=Decimal(str(u["price"])) if u.get("price") else None,
                    price_on_request=not u.get("price"),
                    description=u["desc"],
                )
                created_u += 1
            self.stdout.write(f"  · {proj.name}: added units")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Projects added: {created_p}, units added: {created_u}."))
        self.stdout.write("Images are blank — add them in the admin once photos arrive.")
