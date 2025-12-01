from rest_framework.permissions import BasePermission
from Application.Authentication.auth_utils import get_user_from_request


class IsUserAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(get_user_from_request(request))