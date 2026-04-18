from django.db.models import Q

from .models import Message, MembershipRequest


def notification_counts(request):
    if not request.user.is_authenticated:
        return {"unread_messages": 0, "pending_approvals": 0, "total_notifications": 0}

    unread = Message.objects.filter(
        Q(conversation__user1=request.user) | Q(conversation__user2=request.user),
        is_read=False,
    ).exclude(sender=request.user).count()

    pending = 0
    if hasattr(request.user, "profile"):
        led_cio_ids = request.user.profile.leaderships.filter(
            is_active=True
        ).values_list("cio_id", flat=True)
        if led_cio_ids:
            pending = MembershipRequest.objects.filter(
                cio_id__in=led_cio_ids, status="pending"
            ).count()

    return {
        "unread_messages": unread,
        "pending_approvals": pending,
        "total_notifications": unread + pending,
    }
