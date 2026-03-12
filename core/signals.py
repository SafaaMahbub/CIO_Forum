from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile

User = get_user_model()

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