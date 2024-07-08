from rest_framework import serializers
from .models import User, Organisation

class UserSerializer(serializers.ModelSerializer):
    # userId=serializers.UUIDField(format='hex', read_only=True)
    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'phone']

class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']
