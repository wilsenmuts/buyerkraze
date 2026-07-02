from rest_framework import serializers
from .models import App, AccessKey, Subscription


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ['id', 'name', 'code', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class AccessKeySerializer(serializers.ModelSerializer):
    app_name = serializers.CharField(source='app.name', read_only=True)
    app_code = serializers.CharField(source='app.code', read_only=True)

    class Meta:
        model = AccessKey
        fields = ['id', 'app', 'app_name', 'app_code', 'name', 'key_prefix', 'description',
                  'price', 'duration_days', 'max_requests_per_day', 'max_concurrent_sessions',
                  'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    access_key_name = serializers.CharField(source='access_key.name', read_only=True)
    app_name = serializers.CharField(source='app.name', read_only=True)
    app_code = serializers.CharField(source='app.code', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['id', 'app', 'app_name', 'app_code', 'access_key', 'access_key_name',
                  'user_email', 'user_name', 'generated_key', 'start_date', 'end_date',
                  'status', 'notes', 'days_remaining', 'is_expired', 'created_at']
        read_only_fields = ['id', 'generated_key', 'created_at', 'updated_at']

    def get_days_remaining(self, obj):
        return obj.days_remaining()

    def get_is_expired(self, obj):
        return obj.is_expired()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['app', 'access_key', 'user_email', 'user_name', 'notes']
