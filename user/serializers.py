from rest_framework import serializers
from django.forms import ImageField
from django.contrib.auth import authenticate
from .models import CustomUser, Profile
import phonenumbers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from portfolio.serializers import PortfolioSerializer,CertificateSerializer,EducationSerializer,ExperienceSerializer
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator


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
            raise serializers.ValidationError({'confirm_password': "Passwords do not match"})

        # Terms acceptance
        if not data.get('terms_check'):
            raise serializers.ValidationError({'terms_check': "You must accept the terms and conditions"})

        # Check for existing VERIFIED users
        if CustomUser.objects.filter(username=data['username'], is_verified=True).exists():
            raise serializers.ValidationError({'username': "Username is already taken"})

        if CustomUser.objects.filter(email=data['email'], is_verified=True).exists():
            raise serializers.ValidationError({'email': "Email is already registered"})
        
        # Fix: Changed 'email' to 'cid' in filter
        if CustomUser.objects.filter(cid=data['cid'], is_verified=True).exists():
            raise serializers.ValidationError({'cid': "CID is already registered"})

        return data

    @transaction.atomic
    def create(self, validated_data):
        try:
            validated_data.pop('confirm_password', None)
            email = validated_data['email']
            username = validated_data['username']
            cid = validated_data['cid']

            # Delete existing unverified users with ANY matching unique fields
            CustomUser.objects.filter(
                Q(email=email) |
                Q(username=username) |
                Q(cid=cid),
                is_verified=False
            ).delete()

            # Create the new unverified user
            user = CustomUser.objects.create_user(**validated_data)
            user.is_verified = False
            user.save()
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


class BasicProfileSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'profile_id',
            'profile_picture',
            'banner',
            'bio',
            'address',
            'headline',
        )
        read_only_fields = ('profile_id',)
        

class PrivateUserProfileSerializer(WritableNestedModelSerializer):
    profile = BasicProfileSerializer(required=True)
    
    class Meta:
        model = CustomUser
        fields = (
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name', 
            'phone',
            'role',
            'profile',
        )
        read_only_fields = ('user_id', 'email', 'role')


class DetailProfileSerializer(WritableNestedModelSerializer):
    portfolios = PortfolioSerializer(many=True, required=False, allow_null=True)
    certificates = CertificateSerializer(many=True, required=False, allow_null=True)
    education = EducationSerializer(many=True, required=False, allow_null=True)
    experiences = ExperienceSerializer(many=True, required=False, allow_null=True)
   
   

    class Meta:
        model = Profile
        fields = (
            'profile_id',
            'profile_picture',
            'banner',
            'bio',
            'address',
            'headline',
            'portfolios',
            'certificates',
            'experiences',
            'education',
        )
        read_only_fields = ('profile_id',)


class PublicUserProfileSerializer(WritableNestedModelSerializer):
    profile = DetailProfileSerializer(required=True)
    
    class Meta:
        model = CustomUser
        fields = (
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name', 
            'phone',
            'role',
            'profile',
        )
        read_only_fields = ('user_id', 'email', 'role')


class ProfilePhotoSerializer(serializers.ModelSerializer):
    photo = ImageField(required=False)

    class Meta:
        model = Profile
        fields = ["profile_picture"]


class UserMinimalSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(source='profile.profile_picture', read_only=True)
    headline = serializers.CharField(source='profile.headline', read_only=True)
    address = serializers.CharField(source='profile.address', read_only=True)
    class Meta:
        model = CustomUser
        fields = ('user_id','username', 'address','profile_picture','headline')

class UserBanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['is_banned']
        read_only_fields = ['email', 'username', 'role']
        

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True)
    
    def validate(self,data):
        user = self.context["request"].user
        if not user.check_password(data["password"]):
            raise serializers.ValidationError("Current password is incorrect.")
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError("New password and confirmation do not match.")
        return data
    
    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
    

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    

class PasswordResetSerializer(serializers.Serializer):
    password = serializers.RegexField(
        regex=r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
        write_only=True,
        error_messages={"invalid": ("Password must be at least 8 characters long with at least one capital letter and symbol")},
    )
    confirm_password = serializers.CharField(write_only=True, required=True)
    

class AdminUserCreateSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = CustomUser
    #     fields = ['email', 'username', 'role', 'first_name', 'last_name']
    #     extra_kwargs = {
    #         'password': {'write_only': True, 'required': False}
    #     }

    # def create(self, validated_data):
    #     user = CustomUser.objects.create_user(**validated_data)
    #     user.set_unusable_password()
    #     user.is_verified = False
    #     user.save()
    #     return user
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'role', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False,
                'allow_null': True
            }
        }

    def create(self, validated_data):
        # Explicitly remove password fields if present
        validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)
        
        # Create user with unusable password
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=None,  # This triggers set_unusable_password()
            username=validated_data['username'],
            role=validated_data.get('role'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.is_verified = False
        user.save()
        return user


class AdminUserActivationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Check password match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        # Validate user exists
        try:
            user = CustomUser.objects.get(user_id=data['user_id'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid user ID")
        
        # Validate token
        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired token")
        
        data['user'] = user
        return data