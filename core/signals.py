
from django.contrib.auth import get_user_model # get the currently active User model
from django.db.models.signals import post_save # allow us to run code automatically when certain events happen
from django.dispatch import receiver # used to connect signals to functions
from .models import Profile # Stores user roles


# Get the User model used by Django
User = get_user_model()

# Signal will run whenever a User object is created or saved
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):

    # instance = the specific User object that was just saved
    # created = True if the user was JUST created (not updated)

    # Only create a profile when a NEW user is created
    if created:

        # Get the user's email
        # instance.email might be None, so we protect against that by replacing None with an empty string
        email = (instance.email or "").lower()

        # Check if the email ends with "@virginia.edu"
        if email.endswith("@virginia.edu"):
            role = "student"

        # Otherwise the user is considered a guest
        else:
            role = "guest"

        # Create a Profile object linked to the user
        Profile.objects.create(user=instance, role=role)