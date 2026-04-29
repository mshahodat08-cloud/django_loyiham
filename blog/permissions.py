from rest_framework import permissions

class FaqatMuallifOzgartiradi(permissions.BasePermission):
    """
    Faqat post muallifi tahrirlashi va o'chirishi mumkin
    """

    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS - hamma uchun ruxsat
        if request.method in permissions.SAFE_METHODS:
            return True

        # PUT, PATCH, DELETE - faqat muallif uchun
        return obj.muallif == request.user