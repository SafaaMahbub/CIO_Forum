from django.contrib import admin
from .models import CIO, Profile, CIOLeadership, CIOMembership, MembershipRequest, Review, Comment, Conversation, Message



class CIOLeadershipInline(admin.TabularInline):
    model = CIOLeadership
    extra = 1

class CIOMembershipInline(admin.TabularInline):
    model = CIOMembership
    extra = 1


@admin.register(CIO)
class CIOAdmin(admin.ModelAdmin):
    list_display = (
        "name", "total_leaders", "active_leaders", "inactive_leaders",
        "total_members", "active_members", "inactive_members",
        "avg_career_development", "avg_event_quality",
        "avg_time_commitment", "avg_community_inclusiveness",
    )
    readonly_fields = (
        "avg_career_development", "avg_event_quality",
        "avg_time_commitment", "avg_community_inclusiveness",
    )
    search_fields = ("name", "description")
    inlines = [CIOLeadershipInline, CIOMembershipInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "get_email", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")
    inlines = [CIOLeadershipInline, CIOMembershipInline]

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"


@admin.register(CIOLeadership)
class CIOLeadershipAdmin(admin.ModelAdmin):
    list_display = ("profile", "cio", "is_active")
    list_filter = ("is_active", "cio")
    search_fields = ("profile__user__username", "profile__user__email", "cio__name")

@admin.register(CIOMembership)
class CIOMembershipAdmin(admin.ModelAdmin):
    list_display = ("profile", "cio", "is_active")
    list_filter = ("is_active", "cio")
    search_fields = ("profile__user__username", "profile__user__email", "cio__name")

@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ("profile", "cio", "status", "created_at")
    list_filter = ("status", "cio")
    search_fields = ("profile__user__username", "profile__user__email", "cio__name")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "profile", "cio", "comment", "anonymous",
        "rating_career_development", "rating_event_quality",
        "rating_time_commitment", "rating_community_inclusiveness",
    )
    search_fields = ("profile__user__username", "cio__name", "comment")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "profile", "text", "created_at")
    list_filter = ("review__cio",)
    search_fields = ("profile__user__username", "review__cio__name", "text")
    raw_id_fields = ("review", "profile")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user1", "user2", "updated_at")
    search_fields = ("user1__username", "user2__username")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "created_at")
    search_fields = ("body", "sender__username")