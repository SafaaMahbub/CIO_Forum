# Import Django settings to reference the built-in User model
from django.conf import settings

# Import Django's model system (used to create database tables)
from django.db import models


# Create a Profile model using Django User model
# Allows us to attach roles to users
class Profile(models.Model):

    # ROLE_CHOICES defines the possible roles a user can have.
    # The first value is what gets stored in the database.
    # The second value is the human-readable name shown in Django admin.
    ROLE_CHOICES = [
        ("exec", "CIO Exec Member"),        # CIO executive / club leadership member - may edit CIO pages
        ("student", "UVA Student"),  # UVA student with a virginia.edu email - May leave reviews
        ("guest", "Guest"),          # Non-UVA user (view-only, browse through CIOs)
    ]

    # OneToOneField creates a one-to-one relationship between Profile and User. (one user - one profile)
    # on_delete=models.CASCADE means: If the User is deleted, their Profile will automatically be deleted as well.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # role is a column in the database that stores the user's role.
    # choices=ROLE_CHOICES restricts the value to only the options defined above.
    # default="guest" means that if no role is assigned yet, the user will automatically be considered a guest.
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="guest")
    # Example output: john@virginia.edu - student
    # This makes it much easier to see which user a profile belongs to.
    def __str__(self):
        return f"{self.user.email} - {self.role}"