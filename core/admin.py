from django.contrib import admin
from .models import CIO, Profile, CIOMembership, Review, Conversation, Message



class CIOMembershipInline(admin.TabularInline):
    model = CIOMembership
    extra = 1


@admin.register(CIO)
class CIOAdmin(admin.ModelAdmin):
    list_display = ("name", "total_members", "active_members", "inactive_members")
    search_fields = ("name", "description")
    inlines = [CIOMembershipInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "get_email", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")
    inlines = [CIOMembershipInline]

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"


@admin.register(CIOMembership)
class CIOMembershipAdmin(admin.ModelAdmin):
    list_display = ("profile", "cio", "is_active")
    list_filter = ("is_active", "cio")
    search_fields = ("profile__user__username", "profile__user__email", "cio__name")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("profile","cio","comment")
    search_fields = ("profile__user__username", "cio__name", "comment")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user1", "user2", "updated_at")
    search_fields = ("user1__username", "user2__username")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "created_at")
    search_fields = ("body", "sender__username")