from rest_framework import serializers
from django.contrib.auth.models import User

from sites_function.models import SitesFormat

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user



class SitesFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitesFormat
        fields = ['id', 'title', 'jsoncontent', 'htmlcontent', 'date_time', 'private', 'shared_at']
        extra_kwargs = {
            'title': {'required': False},  
            'jsoncontent': {'required': False},
            'htmlcontent': {'required': False},
            'date_time': {'required': False}, 
            'private': {'required': False},
            'shared_at': {'required': False},         
        }
    # def update(self, instance, validated_data):
    #     # Remove the user field from the validated data if present
    #     validated_data.pop('user', None)
    #     return super().update(instance, validated_data)