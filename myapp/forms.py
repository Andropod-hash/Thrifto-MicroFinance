from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, KYC
from django.core.exceptions import ValidationError  

class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class KYCForm(forms.ModelForm):
    confirm_kyc_email = forms.EmailField(required=True, label="Confirm KYC Email")
    confirm_kyc_phone_number = forms.CharField(required=True, label="Confirm KYC Phone Number")

    class Meta:
        model = KYC
        fields = [
            'full_name',
            'kyc_email', 'confirm_kyc_email', 
            'kyc_phone_number', 'confirm_kyc_phone_number', 
            'address', 'city', 'country', 'file_upload', 'employer', 'salary_range',
            'email_confirmed', 'phone_number_confirmed', 'terms_agreed', 'kyc_confirmed'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'kyc_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'kyc_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'file_upload': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'employer': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_range': forms.Select(attrs={'class': 'form-control'}),
            'email_confirmed': forms.CheckboxInput(),
            'phone_number_confirmed': forms.CheckboxInput(),
            'terms_agreed': forms.CheckboxInput(),
            'kyc_confirmed': forms.CheckboxInput(),
        }

        error_messages = {
            'kyc_email': {'required': 'KYC email is required.'},
            'confirm_kyc_email': {'required': 'Confirmation KYC email is required.'},
            'kyc_phone_number': {'required': 'KYC phone number is required.'},
            'confirm_kyc_phone_number': {'required': 'Confirmation KYC phone number is required.'},
            'address': {'required': 'Address is required.'},
            'city': {'required': 'City is required.'},
            'country': {'required': 'Country is required.'},
            'employer': {'required': 'Employer information is required.'},
            'salary_range': {'required': 'Salary range is required.'},
            'terms_agreed': {'required': 'You must agree to the terms.'},
            'kyc_confirmed': {'required': "Kyc confirmed field is required"}
        }

    def clean(self):
        cleaned_data = super().clean()
        
        kyc_email = cleaned_data.get('kyc_email')
        confirm_kyc_email = cleaned_data.get('confirm_kyc_email')
        kyc_phone_number = cleaned_data.get('kyc_phone_number')
        confirm_kyc_phone_number = cleaned_data.get('confirm_kyc_phone_number')
        terms_agreed = cleaned_data.get('terms_agreed')
        kyc_confirmed = cleaned_data.get('kyc_confirmed')  

        # Check if KYC is already confirmed
        if self.instance and self.instance.kyc_confirmed:
            raise ValidationError('KYC has already been confirmed. Please use the KYC update endpoint to modify your details.')

        # Email validations
        if kyc_email and confirm_kyc_email and kyc_email != confirm_kyc_email:
            self.add_error('kyc_email', "KYC emails do not match.")

        # Phone number validations
        if kyc_phone_number and confirm_kyc_phone_number and kyc_phone_number != confirm_kyc_phone_number:
            self.add_error('kyc_phone_number', "KYC phone numbers do not match.")

        # Check if terms agreed is not checked
        if not terms_agreed:
            self.add_error('terms_agreed', "You must agree to the terms.")

        # Check if KYC confirmation checkbox is checked
        if not kyc_confirmed:
            self.add_error('kyc_confirmed', "You must click on the confirm button.")

        # If there are any form errors, set kyc_confirmed to False
        if self.errors:
            cleaned_data['kyc_confirmed'] = False

        return cleaned_data



class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class TwoFAForm(forms.Form):
    two_fa_code = forms.CharField(max_length=10, required=True)  
    user_id = forms.IntegerField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        two_fa_code = cleaned_data.get('two_fa_code')
        user_id = cleaned_data.get('user_id')

        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            raise forms.ValidationError("User does not exist.")

        print(f"Debug Info: User's 2FA code: {user.two_fa_code}, Expires at: {user.two_fa_code_expires}")
        print(f"Debug Info: Current time: {timezone.now()}")

        if user.two_fa_code != two_fa_code:
            raise forms.ValidationError('Invalid 2FA code.')

        if timezone.now() > user.two_fa_code_expires:
            raise forms.ValidationError('2FA code has expired.')

        cleaned_data['user'] = user
        return cleaned_data

