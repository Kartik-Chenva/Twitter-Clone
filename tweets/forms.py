from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Tweet, Comment

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']

class TweetForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': "What's happening?"}),
        max_length=280
    )
    image = forms.ImageField(required=False)
    
    class Meta:
        model = Tweet
        fields = ['content', 'image']

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'placeholder': "Enter the new comment content here...",
            'class': 'form-control',
            'style': 'border-radius: 10px; resize: vertical;'
        }),
        max_length=280
    )
    
    class Meta:
        model = Comment
        fields = ['content']


from django import forms
from .models import Follow
from django.contrib.auth.models import User

class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ['follower', 'following']
        widgets = {
            'follower': forms.Select(attrs={
                'class': 'form-select',
                'style': 'border-radius: 10px; border: 2px solid #e9ecef; transition: all 0.3s ease;'
            }),
            'following': forms.Select(attrs={
                'class': 'form-select',
                'style': 'border-radius: 10px; border: 2px solid #e9ecef; transition: all 0.3s ease;'
            })
        }


from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'profile_picture']

class AdminProfileEditForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user fields
            user = profile.user
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.save()
            profile.save()
        return profile

class AdminTweetEditForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': "What's happening?"}),
        max_length=280,
        required=True
    )
    
    class Meta:
        model = Tweet
        fields = ['content', 'image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
    
    def save(self, commit=True):
        tweet = super().save(commit=False)
        if commit:
            # Update user if username changed
            new_username = self.cleaned_data['username']
            if new_username != tweet.user.username:
                # Find user by new username
                from django.contrib.auth.models import User
                try:
                    new_user = User.objects.get(username=new_username)
                    tweet.user = new_user
                except User.DoesNotExist:
                    # If user doesn't exist, keep the original user
                    pass
            tweet.save()
        return tweet

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'border-radius: 8px; border: 1px solid #dee2e6; transition: all 0.2s ease;'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'style': 'border-radius: 8px; border: 1px solid #dee2e6; transition: all 0.2s ease;'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'border-radius: 8px; border: 1px solid #dee2e6; transition: all 0.2s ease;'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'border-radius: 8px; border: 1px solid #dee2e6; transition: all 0.2s ease;'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 18px; height: 18px;'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 18px; height: 18px;'
            })
        }
