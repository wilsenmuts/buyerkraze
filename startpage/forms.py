from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import EventSubscription, Article

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = EventSubscription
        fields = ('user_name', 'user_email', 'user_phone', 'additional_details')
        widgets = {
            'additional_details': forms.Textarea(attrs={'rows': 4}),
        }

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'featured_image', 'top_image', 'editor_mode']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-300 rounded-xl p-4 text-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all',
                'placeholder': 'Enter your article title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full border-2 border-gray-300 rounded-xl p-4 text-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all font-mono',
                'placeholder': 'Write your article content here...',
                'rows': 20,
                'id': 'article-content-editor'
            }),
            'editor_mode': forms.Select(attrs={
                'class': 'w-full border-2 border-gray-300 rounded-xl p-3 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all'
            }),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        editor_mode = self.cleaned_data.get('editor_mode')
        # In modern mode, ensure content has basic HTML structure if needed
        if editor_mode == 'modern' and content:
            # Strip surrounding whitespace but preserve HTML
            content = content.strip()
        return content