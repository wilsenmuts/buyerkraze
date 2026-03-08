from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from django.db.models import F
from django.shortcuts import get_object_or_404
from .models import Article, ArticleInteraction
from .serializers import ArticleSerializer, ArticleCreateSerializer
from .authentication import APIKeyAuthentication

class ArticleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleCreateSerializer
        return ArticleSerializer
    
    def get_authenticators(self):
        if self.request.method == 'POST':
            return [APIKeyAuthentication()]
        return []

class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        Article.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@api_view(['POST'])
def article_like(request, pk):
    article = get_object_or_404(Article, pk=pk)
    session_id = request.META.get('REMOTE_ADDR', '') + request.headers.get('User-Agent', '')[:50]
    
    # Check if user already interacted
    interaction, created = ArticleInteraction.objects.get_or_create(
        article=article,
        session_id=session_id,
        defaults={'interaction_type': 'like'}
    )
    
    if not created:
        if interaction.interaction_type == 'like':
            return Response({'error': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Change from dislike to like
            Article.objects.filter(pk=pk).update(dislikes=F('dislikes') - 1, likes=F('likes') + 1)
            interaction.interaction_type = 'like'
            interaction.save()
    else:
        Article.objects.filter(pk=pk).update(likes=F('likes') + 1)
    
    article.refresh_from_db()
    return Response({
        'likes': article.likes,
        'dislikes': article.dislikes
    })

@api_view(['POST'])
def article_dislike(request, pk):
    article = get_object_or_404(Article, pk=pk)
    session_id = request.META.get('REMOTE_ADDR', '') + request.headers.get('User-Agent', '')[:50]
    
    # Check if user already interacted
    interaction, created = ArticleInteraction.objects.get_or_create(
        article=article,
        session_id=session_id,
        defaults={'interaction_type': 'dislike'}
    )
    
    if not created:
        if interaction.interaction_type == 'dislike':
            return Response({'error': 'Already disliked'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Change from like to dislike
            Article.objects.filter(pk=pk).update(likes=F('likes') - 1, dislikes=F('dislikes') + 1)
            interaction.interaction_type = 'dislike'
            interaction.save()
    else:
        Article.objects.filter(pk=pk).update(dislikes=F('dislikes') + 1)
    
    article.refresh_from_db()
    return Response({
        'likes': article.likes,
        'dislikes': article.dislikes
    })
