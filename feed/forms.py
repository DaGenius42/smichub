from django import forms
from .models import Post
from .models import Comments
from .models import CustomUser
from .models import Vote

class CustomUserForm(forms.ModelForm):
    
    email = forms.EmailField(
        required=True,
        help_text="Must be school email - @bjsmicschool.com",
        widget=forms.EmailInput(attrs={
            'placeholder': 'student_id@bjsmicschool.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
        label="Password"
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Enter your username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Enter your SCHOOL email"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email.endswith('@bjsmicschool.com'):
            raise forms.ValidationError(
                f'Please use the school email'
            )
        
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        
        return email
    

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['category', 'title', 'body', 'file_attached']
        widgets = {
            'file_attached': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'title': forms.TextInput(attrs={'placeholder': 'Title for your post', 'maxlength': 120}),
            'body': forms.Textarea(attrs={'placeholder': 'Write your post here...', 'rows': 15, 'maxlength': 5000}),
        }

    def clean_body(self):
        body = self.cleaned_data.get('body', '')
        if len(body) > 5000:
            raise forms.ValidationError('Post body must be 5000 characters or fewer.')
        return body

class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Write your comment here...', 'rows': 2}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'bio', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Your username'}),
            'bio': forms.Textarea(attrs={
                'placeholder': 'Tell people about yourself...',
                'rows': 4,
                'maxlength': 200,
            }),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        if len(bio) > 200:
            raise forms.ValidationError('Bio must be 200 characters or fewer.')
        return bio

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Write your vote here...', 'rows': 2}),
        }