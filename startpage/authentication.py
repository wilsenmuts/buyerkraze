from rest_framework import authentication
from rest_framework import exceptions
from .models import APIKey

class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None
        
        try:
            key_obj = APIKey.objects.get(key=api_key, is_active=True)
            return (None, key_obj)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API Key')
