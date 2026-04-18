# Import Django settings to reference the built-in User model
from django.conf import settings



# Import Django's model system (used to create database tables)
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


def ordered_user_pair(user_a, user_b):
    """Return (lower_pk_user, higher_pk_user) for a stable 1:1 conversation key."""
    if user_a.pk == user_b.pk:
        raise ValueError("Cannot create a conversation with the same user twice.")
    return (user_a, user_b) if user_a.pk < user_b.pk else (user_b, user_a)


def get_or_create_conversation(user_a, user_b):
    u1, u2 = ordered_user_pair(user_a, user_b)
    conv, _created = Conversation.objects.get_or_create(user1=u1, user2=u2)
    return conv


def cio_upload_path(instance, filename):
    cio = instance.cio
    return f"cio_uploads/{cio.id}_{slugify(cio.name)}/{filename}"

class CIO(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cio_profile_picture = models.ImageField(upload_to="cio_profile_pictures")

    avg_career_development = models.FloatField(null=True, blank=True)
    avg_event_quality = models.FloatField(null=True, blank=True)
    avg_time_commitment = models.FloatField(null=True, blank=True)
    avg_community_inclusiveness = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

    def total_leaders(self):
        return self.leaderships.count()

    def active_leaders(self):
        return self.leaderships.filter(is_active=True).count()

    def inactive_leaders(self):
        return self.leaderships.filter(is_active=False).count()

    def update_average_ratings(self):
        reviews = self.review_set.all()
        for field, avg_field in [
            ("rating_career_development", "avg_career_development"),
            ("rating_event_quality", "avg_event_quality"),
            ("rating_time_commitment", "avg_time_commitment"),
            ("rating_community_inclusiveness", "avg_community_inclusiveness"),
        ]:
            rated = reviews.filter(**{f"{field}__isnull": False})
            if rated.exists():
                total = sum(getattr(r, field) for r in rated)
                setattr(self, avg_field, round(total / rated.count(), 2))
            else:
                setattr(self, avg_field, None)
        self.save()




#Uploading  images and files
# cio: links the file to a CIO
# uploaded_by: stores who uploaded it
# title: lets you name the file
# file: stores the actual uploaded file
# uploaded_at: timestamp
class UploadedFile(models.Model):
    cio = models.ForeignKey("CIO", on_delete=models.CASCADE, related_name="uploads")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to=cio_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



# Create a Profile model using Django User model
# Allows us to attach roles to users
class Profile(models.Model):

    # ROLE_CHOICES defines the possible roles a user can have.
    # The first value is what gets stored in the database.
    # The second value is the human-readable name shown in Django admin.
    ROLE_CHOICES = [
        ("student", "UVA Student"),  # UVA student with a virginia.edu email - May leave reviews
        ("guest", "Guest"),          # Non-UVA user (view-only, browse through CIOs)
        ("user_admin", "User Administrator")      # User Admin role specified in Sprint 5
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
        through="CIOLeadership",
        related_name="profiles",
        blank=True
    )

    profile_picture = models.ImageField(upload_to="profile_pictures", default="profile_pictures/defaultPic.jpg")

    # Example output: john@virginia.edu - student
    # This makes it much easier to see which user a profile belongs to.
    @property
    def is_exec(self):
        return self.leaderships.filter(is_active=True).exists()

    def __str__(self):
        return f"{self.user.email} - {self.role}"


# Automate profile creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        email = instance.email.lower()
        rl = "student"  if email.endswith("@virginia.edu") else "guest"
        Profile.objects.create(user=instance, role=rl)
    else:
        Profile.objects.get_or_create(user=instance)



@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    cio = models.ForeignKey(CIO, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    anonymous = models.BooleanField(default=False)

    rating_career_development = models.IntegerField(
        choices=RATING_CHOICES, null=True, blank=True,
    )
    rating_event_quality = models.IntegerField(
        choices=RATING_CHOICES, null=True, blank=True,
    )
    rating_time_commitment = models.IntegerField(
        choices=RATING_CHOICES, null=True, blank=True,
    )
    rating_community_inclusiveness = models.IntegerField(
        choices=RATING_CHOICES, null=True, blank=True,
    )

    def __str__(self):
        return f"{self.profile.user.username} - {self.cio.name}"

    class Meta:
        unique_together = ("profile", "cio")

class CIOLeadership(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="leaderships"
    )
    cio = models.ForeignKey(
        CIO,
        on_delete=models.CASCADE,
        related_name="leaderships"
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


class Conversation(models.Model):
    """One DM thread between two users. user1_id is always less than user2_id."""

    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dm_conversations_as_user1",
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dm_conversations_as_user2",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user1", "user2"], name="unique_dm_user_pair"),
            models.CheckConstraint(
                check=models.Q(user1_id__lt=models.F("user2_id")),
                name="dm_user_order",
            ),
        ]

    def __str__(self):
        return f"DM {self.user1_id} ↔ {self.user2_id}"

    def other_participant(self, user):
        if user.pk == self.user1_id:
            return self.user2
        if user.pk == self.user2_id:
            return self.user1
        raise ValueError("User is not a participant in this conversation.")


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_dm_messages",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender_id}: {self.body[:40]}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Conversation.objects.filter(pk=self.conversation_id).update(
            updated_at=timezone.now()
        )