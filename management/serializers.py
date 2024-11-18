from rest_framework import serializers

from .models import User, Books


class UserSignupSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        password = validated_data.pop("password")
        is_active = validated_data.pop("is_active")
        user = User.objects.create(**validated_data)
        print(f"\n user - {validated_data}\n")
        user.set_password(password)
        user.save()
        return user

class BooksSerializer(serializers.ModelSerializer):

    class Meta:
        model = Books
        fields = "__all__"
        
            