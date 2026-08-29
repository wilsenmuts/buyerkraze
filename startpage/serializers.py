from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'published_date', 'updated_date', 
                  'featured_image', 'top_image', 'view_count', 'likes', 'dislikes',
                  'editor_mode', 'author']
        read_only_fields = ['id', 'published_date', 'updated_date', 'view_count', 'likes', 'dislikes', 'author']

class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'content', 'featured_image', 'top_image', 'editor_mode']
