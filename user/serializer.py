from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Profile
import phonenumbers

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)
    class Meta:
        model = CustomUser
        fields = ('token')

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    confirm_password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('user_id', 'username', 'email', 'password', 'confirm_password','cid',
                 'first_name', 'last_name', 'phone', 'role', 'terms_check')
        extra_kwargs = {
            'password': {'write_only': True},
            'terms_check': {'required': True},
        }

    def validate_phone(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required")

        try:
            # First try parsing with the given number
            parsed_number = phonenumbers.parse(value)
            
            # If number doesn't have country code, try with default country (e.g., 'US')
            if not value.startswith('+'):
                parsed_number = phonenumbers.parse(value, "BT")  # Change 'US' to your default country

            # Validate the phone number
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError("Invalid phone number format")

            # Format the number in E.164 format (standardized format)
            formatted_number = phonenumbers.format_number(
                parsed_number, 
                phonenumbers.PhoneNumberFormat.E164
            )
            
            # Store the formatted number
            return formatted_number

        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Please enter a valid phone number with country code")

    def validate(self, data):
        # Password validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match"
            })

        # Terms acceptance
        if not data.get('terms_check'):
            raise serializers.ValidationError({
                'terms_check': "You must accept the terms and conditions"
            })

        # Check for existing users
        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({
                'username': "Username is already taken"
            })

        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': "Email is already registered"
            })
        
        if CustomUser.objects.filter(email=data['cid']).exists():
            raise serializers.ValidationError({
                'cid': "cid is already registered"
            })

        return data

    def create(self, validated_data):
        """Create a new user with validated data."""
        try:
            # Remove confirm_password field
            validated_data.pop('confirm_password', None)
            
            # Create the user
            user = CustomUser.objects.create_user(**validated_data)
            return user
            
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create user: {str(e)}")

    def to_representation(self, instance):
        """Customize the output representation of the user."""
        data = super().to_representation(instance)
        
        # Format phone number for display if needed
        try:
            parsed_number = phonenumbers.parse(instance.phone)
            data['phone'] = phonenumbers.format_number(
                parsed_number,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        except (phonenumbers.NumberParseException, AttributeError):
            pass
            
        return data

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        if user.is_banned:
            raise serializers.ValidationError('This account has been banned')
        if not user.is_verified:
            raise serializers.ValidationError('Please verify your email first')
        return data

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('profile_id', 'profile_picture', 'banner', 'bio', 'address','headline')

class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    
    class Meta:
        model = CustomUser
        fields = ('user_id', 'username', 'email', 'first_name', 'last_name', 
                 'phone', 'role', 'profile','address',)
        read_only_fields = ('user_id', 'email', 'role')

class UserMinimalSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(source='profile.profile_picture', read_only=True)
    headline = serializers.CharField(source='profile.headline', read_only=True)
    class Meta:
        model = CustomUser
        fields = ('user_id','username', 'address','profile_picture','headline')
