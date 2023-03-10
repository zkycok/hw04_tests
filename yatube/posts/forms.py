from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        help_text = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        labels = {
            "group": "Группа",
            "text": "Текст"
        }
