from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class CustomUserChangeForm(forms.ModelForm):
    """
    A form for updating existing users by an admin.
    """
    password = None  # Admins should use a separate process for password resets

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'role', 'is_active', 'avatar_url')
        widgets = {
            'avatar_url': forms.URLInput(attrs={'placeholder': 'https://example.com/image.png'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'