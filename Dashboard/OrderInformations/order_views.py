from .order_serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from Dashboard.permissions import IsSuperUser

from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

class OrderListView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        orders = UserOrderModel.objects.all().order_by("-created")

        # --------------------
        # SEARCH
        # --------------------

        query = request.query_params.get("q")
        if query:
            orders = orders.filter(
                Q(order_id__icontains=query) |
                Q(razorpay_order_id__icontains=query) |
                Q(status__icontains=query) |
                Q(user__username__icontains=query) |
                Q(user__email__icontains=query)
            )

        # --------------------
        # DATE FILTERS
        # --------------------

        date_filter = request.query_params.get("date")
        now = timezone.now()

        if date_filter == "today":
            orders = orders.filter(created__date=now.date())

        elif date_filter == "month":
            orders = orders.filter(
                created__year=now.year,
                created__month=now.month
            )

        elif date_filter == "year":
            orders = orders.filter(created__year=now.year)

        # --------------------
        # CUSTOM DATE RANGE
        # --------------------

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                orders = orders.filter(created__range=(start, end))
            except ValueError:
                pass  # ignore invalid date format

        serializer = DashboardOrderSerializer(
            orders, many=True, context={"request": request}
        )
        return Response(serializer.data)

class OrderDetailView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, order_id):    
        order = UserOrderModel.objects.get(order_id=order_id)
        serializer = DashboardOrderSerializer(order, context={"request": request})
        return Response(serializer.data)

class OrderUpdateView(APIView):
    permission_classes = [IsSuperUser]

    def patch(self, request, order_id):
        order = UserOrderModel.objects.get(order_id=order_id)
        serializer = DashboardOrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDeleteView(APIView):
    permission_classes = [IsSuperUser]
    
    def delete(self, request, order_id):
        order = UserOrderModel.objects.get(order_id=order_id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
