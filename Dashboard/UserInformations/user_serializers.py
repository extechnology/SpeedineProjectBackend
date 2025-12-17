from rest_framework import serializers
from Application.UserServices.user_models import User
from Application.UserServices.user_models import ContactModel

class DashboardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class DashboardContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactModel
        fields = '__all__'