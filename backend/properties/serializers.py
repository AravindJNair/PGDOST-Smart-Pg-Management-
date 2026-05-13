from rest_framework import serializers
from .models import Property, Room, PropertyImage, Review, Inquiry
from django.db.models import Avg


class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url', 'caption', 'is_primary', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None


class RoomSerializer(serializers.ModelSerializer):
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'property', 'room_number', 'room_type', 'room_type_display',
            'total_beds', 'available_beds', 'rent_per_month',
            'is_available', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'property', 'is_available', 'created_at']


class PropertySerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    rooms = RoomSerializer(many=True, read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    primary_image_url = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'owner', 'owner_username', 'name', 'description',
            'property_type', 'property_type_display',
            'address', 'city', 'state', 'pincode', 'phone', 'email',
            'has_wifi', 'has_ac', 'has_food', 'has_parking', 'has_laundry', 'has_gym',
            'custom_amenities',
            'lifestyle_highlights', 'suitable_for', 'overview_custom_text',
            'smoking_policy', 'visitor_rules', 'gate_closing_time', 'drinking_rules', 'quiet_hours',
            'nearby_landmarks', 'nearby_colleges', 'nearby_transit', 'google_maps_url', 'nearby_places',
            'pricing_monthly_rent', 'pricing_security_deposit', 'pricing_maintenance_charge', 'pricing_food_charge',
            'whatsapp_number', 'alternate_contact', 'videos',
            'is_approved', 'approved_at',
            'created_at', 'updated_at', 'rooms', 'images', 'primary_image_url', 'avg_rating'
        ]
        read_only_fields = ['id', 'owner', 'is_approved', 'approved_at', 'created_at', 'updated_at']

    def get_primary_image_url(self, obj):
        request = self.context.get('request')
        primary = obj.images.filter(is_primary=True).first() or obj.images.first()
        if primary and primary.image:
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None


class PropertyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for marketplace listing (no rooms detail)."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    room_count = serializers.SerializerMethodField()
    min_rent = serializers.SerializerMethodField()
    primary_image_url = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'owner_username', 'name', 'description',
            'property_type', 'property_type_display',
            'address', 'city', 'state', 'pincode',
            'has_wifi', 'has_ac', 'has_food', 'has_parking', 'has_laundry', 'has_gym',
            'room_count', 'min_rent', 'primary_image_url', 'avg_rating', 'created_at'
        ]

    def get_room_count(self, obj):
        return obj.rooms.count()

    def get_min_rent(self, obj):
        rooms = obj.rooms.all()
        if rooms.exists():
            return min(r.rent_per_month for r in rooms)
        return None

    def get_primary_image_url(self, obj):
        request = self.context.get('request')
        primary = obj.images.filter(is_primary=True).first() or obj.images.first()
        if primary and primary.image:
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None

    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    review_date = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'property', 'user', 'username', 'rating', 'review_text',
            'stay_duration', 'is_verified_resident', 'created_at', 'review_date'
        ]
        read_only_fields = ['id', 'property', 'user', 'is_verified_resident', 'created_at', 'review_date']

    def get_review_date(self, obj):
        return obj.created_at.date().isoformat() if obj.created_at else None


class InquirySerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)

    class Meta:
        model = Inquiry
        fields = ['id', 'property', 'property_name', 'sender_name', 'sender_email', 'sender_phone', 'message', 'created_at']
        read_only_fields = ['id', 'property', 'created_at']
