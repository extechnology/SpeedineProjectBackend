from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from Application.UserServices.user_models import User
from Dashboard.UserInformations.user_serializers import DashboardUserSerializer,DashboardContactSerializer
from Dashboard.permissions import IsSuperUser
from Application.UserServices.user_models import ContactModel

class UserListView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        users = User.objects.all().order_by("-date_joined")

        # --------------------
        # SEARCH
        # --------------------
        query = request.query_params.get("q")
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query) |
                Q(fullname__icontains=query)
            )

        # --------------------
        # DATE FILTERS
        # --------------------
        date_filter = request.query_params.get("date")
        now = timezone.now()

        if date_filter == "today":
            users = users.filter(date_joined__date=now.date())

        elif date_filter == "month":
            users = users.filter(
                date_joined__year=now.year,
                date_joined__month=now.month
            )

        elif date_filter == "year":
            users = users.filter(date_joined__year=now.year)

        # --------------------
        # CUSTOM DATE RANGE
        # --------------------
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                users = users.filter(date_joined__range=(start, end))
            except ValueError:
                pass

        # --------------------
        # STATUS FILTERS
        # --------------------
        is_active = request.query_params.get("is_active")
        if is_active in ["true", "false"]:
            users = users.filter(is_active=is_active == "true")

        is_email_verified = request.query_params.get("is_email_verified")
        if is_email_verified in ["true", "false"]:
            users = users.filter(is_email_verified=is_email_verified == "true")

        is_phone_verified = request.query_params.get("is_phone_verified")
        if is_phone_verified in ["true", "false"]:
            users = users.filter(is_phone_verified=is_phone_verified == "true")

        serializer = DashboardUserSerializer(
            users, many=True, context={"request": request}
        )
        return Response(serializer.data)


class ContactListView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        contacts = ContactModel.objects.all().order_by("-created")
        
        q = request.query_params.get("q")
        if q:
            contacts = contacts.filter(
                Q(name__icontains=q) |
                Q(email__icontains=q) |
                Q(message__icontains=q)
            )
        
        date_filter = request.query_params.get("date")
        now = timezone.now()

        if date_filter == "today":
            contacts = contacts.filter(created__date=now.date())

        elif date_filter == "month":
            contacts = contacts.filter(
                created__year=now.year,
                created__month=now.month
            )

        elif date_filter == "year":
            contacts = contacts.filter(created__year=now.year)

        # --------------------
        # CUSTOM DATE RANGE
        # --------------------
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                contacts = contacts.filter(created__range=(start, end))
            except ValueError:
                pass

        serializer = DashboardContactSerializer(
            contacts, many=True, context={"request": request}
        )
        return Response(serializer.data)