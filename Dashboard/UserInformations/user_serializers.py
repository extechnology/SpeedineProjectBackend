from rest_framework import serializers
from Application.UserServices.user_models import User


class DashboardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
