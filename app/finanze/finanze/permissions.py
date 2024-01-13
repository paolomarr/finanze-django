from rest_framework import permissions


class IsOwnerOrDeny(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to see it.
    """

    def has_object_permission(self, request, view, obj):
        # Any kind of permissions are only allowed to the owner of the snippet.
        return request.user.is_authenticated and obj.user == request.user

class IsAuthenticatedSelfUser(permissions.BasePermission):
    """ 
    Custom permission for User views: specific user info can be viewed by the user itself only 
    (or admin, but we don't take that into account here, as there's a default permission set for that)
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj