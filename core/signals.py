from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models import Profile

User = get_user_model()


# Default CIO categories seeded automatically after every `migrate`.
# Edit this list to add / remove defaults. Existing rows with the same slug
# are left untouched, so admins can rename or recolor via the admin.
DEFAULT_CATEGORIES = [
    {"name": "Academic", "slug": "academic", "color": "#2a6fb5"},
    {"name": "Service",  "slug": "service",  "color": "#16a34a"},
    {"name": "Cultural", "slug": "cultural", "color": "#9333ea"},
    {"name": "Sports",   "slug": "sports",   "color": "#ea580c"},
]


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    email = (instance.email or "").lower()

    if email.endswith("@virginia.edu"):
        default_role = "student"
    else:
        default_role = "guest"

    Profile.objects.get_or_create(
        user=instance,
        defaults={"role": default_role}
    )


@receiver(post_migrate)
def seed_default_categories(sender, **kwargs):
    """Ensure the built-in CIO categories exist after each migrate."""
    if getattr(sender, "name", None) != "core":
        return
    try:
        Category = django_apps.get_model("core", "Category")
    except LookupError:
        return
    for cat in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            slug=cat["slug"],
            defaults={"name": cat["name"], "color": cat["color"]},
        )