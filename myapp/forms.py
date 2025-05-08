from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Order,PDFCollection, UserProfile, Community, CommunityPost



class CustomUserCreationForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        # comfirming entered password\
        if password != confirm_password:
            raise ValidationError("The two password fields must match.")
        
        return cleaned_data

    def save(self):
        name = self.cleaned_data['name']
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        # creating and saving user 
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = name
        user.save()

        return user


class CheckoutForm(forms.ModelForm):
    account_name = forms.CharField(max_length=100, required=False)  
    username = forms.CharField(max_length=100, required=False)  

    class Meta:
        model = Order
        fields = ['delivery_address']  

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields['account_name'].initial = user.get_full_name()
            self.fields['username'].initial = user.username


class ExpertNoteForm(forms.Form):
    pdf_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'custom_file_input',  
            'accept': '.pdf', 
        })
    )


class PDFCollectionForm(forms.ModelForm):
    class Meta:
        model = PDFCollection
        fields = ['file']



class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image']

class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'description', 'community_id']

class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['message', 'file']