from rest_framework import serializers
from .models import Ticket, TicketReply


class TicketReplySerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = TicketReply
        fields = ['id', 'ticket', 'author', 'author_username', 'message', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TicketSerializer(serializers.ModelSerializer):
    raised_by_username = serializers.CharField(source='raised_by.username', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'raised_by', 'raised_by_username', 'property', 'property_name',
            'title', 'description', 'category', 'category_display',
            'priority', 'priority_display', 'status', 'status_display',
            'owner_response', 'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = ['id', 'raised_by', 'status', 'owner_response', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['raised_by'] = self.context['request'].user
        return super().create(validated_data)


class TicketStatusUpdateSerializer(serializers.ModelSerializer):
    """Owner updates status of a ticket."""
    class Meta:
        model = Ticket
        fields = ['status', 'owner_response']
