from django import forms
from .models import Post
from .models import Comments

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['category','title', 'body']
        widegets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title for your post'}),
            'body': forms.Textarea(attrs={'placeholder': 'Write your post here...', 'rows': 15}),

        }

class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Write your comment here...', 'rows': 5}),
        }