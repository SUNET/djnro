from rest_framework import serializers

from edumanage.models import Institution
from edumanage.models import ServiceLoc


class ServiceLocSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLoc
        fields = '__all__'


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'
