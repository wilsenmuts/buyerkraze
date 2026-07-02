from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import App, AccessKey, Subscription
from .serializers import AppSerializer, AccessKeySerializer, SubscriptionSerializer, SubscriptionCreateSerializer


# ─── App Endpoints ───────────────────────────────────────────────

class AppListAPIView(generics.ListAPIView):
    """List all active applications."""
    queryset = App.objects.filter(is_active=True)
    serializer_class = AppSerializer
    permission_classes = [AllowAny]


# ─── Access Key / Tier Endpoints ─────────────────────────────────

class AccessKeyListCreateAPIView(generics.ListCreateAPIView):
    """List all access key tiers or create a new one."""
    queryset = AccessKey.objects.filter(is_active=True).select_related('app')
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        return AccessKeySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]


class AccessKeyDetailAPIView(generics.RetrieveAPIView):
    """Retrieve details of a specific access key tier."""
    queryset = AccessKey.objects.all()
    serializer_class = AccessKeySerializer
    permission_classes = [AllowAny]


class TiersByAppCodeAPIView(generics.ListAPIView):
    """List active tiers for a specific app by its app code."""
    serializer_class = AccessKeySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        app_code = self.kwargs.get('app_code')
        return AccessKey.objects.filter(
            app__code=app_code,
            is_active=True
        ).select_related('app')


# ─── Subscription Endpoints ──────────────────────────────────────

class SubscriptionListCreateAPIView(generics.ListCreateAPIView):
    """List all subscriptions or create a new one."""
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubscriptionCreateSerializer
        return SubscriptionSerializer

    def get_queryset(self):
        qs = Subscription.objects.select_related('access_key', 'app').all()
        status_filter = self.request.query_params.get('status')
        app_code = self.request.query_params.get('app_code')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if app_code:
            qs = qs.filter(app__code=app_code)
        return qs

    def perform_create(self, serializer):
        subscription = serializer.save()
        return subscription


class SubscriptionDetailAPIView(generics.RetrieveAPIView):
    """Retrieve details of a specific subscription."""
    queryset = Subscription.objects.select_related('access_key', 'app').all()
    serializer_class = SubscriptionSerializer
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([IsAdminUser])
def cancel_subscription(request, pk):
    """Cancel an active subscription."""
    subscription = get_object_or_404(Subscription, pk=pk)
    if subscription.status == 'cancelled':
        return Response({'error': 'Subscription is already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
    if subscription.status == 'expired':
        return Response({'error': 'Subscription is already expired'}, status=status.HTTP_400_BAD_REQUEST)
    subscription.status = 'cancelled'
    subscription.save()
    serializer = SubscriptionSerializer(subscription)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def validate_key(request):
    """Validate a subscription key and return its details."""
    key = request.query_params.get('key')
    if not key:
        return Response({'error': 'key parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    subscription = get_object_or_404(Subscription, generated_key=key)

    if subscription.status != 'active':
        return Response({
            'valid': False,
            'status': subscription.status,
            'error': f'Subscription is {subscription.status}'
        }, status=status.HTTP_400_BAD_REQUEST)

    if subscription.is_expired():
        subscription.status = 'expired'
        subscription.save()
        return Response({
            'valid': False,
            'status': 'expired',
            'error': 'Subscription has expired'
        }, status=status.HTTP_400_BAD_REQUEST)

    serializer = SubscriptionSerializer(subscription)
    return Response({
        'valid': True,
        'subscription': serializer.data
    })
