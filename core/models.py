# Import Django settings to reference the built-in User model
from django.conf import settings

# Import Django's model system (used to create database tables)
from django.db import models

from django.contrib.auth.models import User

class CIO(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def total_members(self):
        return self.memberships.count()

    def active_members(self):
        return self.memberships.filter(is_active=True).count()

    def inactive_members(self):
        return self.memberships.filter(is_active=False).count()


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

    cios = models.ManyToManyField(
        CIO,
        through="CIOMembership",
        related_name="profiles",
        blank=True
    )

    # Example output: john@virginia.edu - student
    # This makes it much easier to see which user a profile belongs to.
    def __str__(self):
        return f"{self.user.email} - {self.role}"
    
class CIOMembership(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    cio = models.ForeignKey(
        CIO,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("profile", "cio")

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.profile.user.username} - {self.cio.name} ({status})"

    def save(self, *args, **kwargs):
        if self.profile.role == "guest":
            raise ValueError("Guest users cannot join CIOs.")
        super().save(*args, **kwargs)