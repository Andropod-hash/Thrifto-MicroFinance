from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True, null=True)

    # Fields for two-factor authentication
    two_fa_code = models.CharField(max_length=6, blank=True, null=True)
    two_fa_verified = models.BooleanField(default=False)
    two_fa_code_expires = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

def validate_file_type(file):
    """Validator to check if the file type is jpg, png, or pdf"""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    ext = os.path.splitext(file.name)[1]  # Get the file extension
    if ext.lower() not in valid_extensions:
        raise ValidationError(_('Invalid file type. Only JPG, PNG, and PDF files are allowed.'))

def validate_file_size(file):
    """Validator to check if the file size is less than or equal to 10MB"""
    max_file_size = 10 * 1024 * 1024  # 10MB in bytes
    if file.size > max_file_size:
        raise ValidationError(_('File size cannot exceed 10MB.'))
       

class KYC(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    kyc_email = models.EmailField()
    kyc_phone_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    employer = models.CharField(max_length=100)
    file_upload = models.FileField(
        upload_to='uploads/',
        validators=[validate_file_type, validate_file_size],
        blank=True,
        null=True,
        help_text="Upload a JPG, PNG, or PDF file. Max size: 10MB."
    )
    salary_range = models.CharField(max_length=50)  #\
    email_confirmed = models.BooleanField(default=False)
    phone_number_confirmed = models.BooleanField(default=False)
    terms_agreed = models.BooleanField(default=False)
    kyc_confirmed = models.BooleanField(default=False)
    

    def __str__(self):
        return self.full_name

class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_identifier = models.CharField(max_length=255)  
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.device_identifier} - {self.ip_address}"

# class Group(models.Model):
#     name = models.CharField(max_length=100)
#     admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_groups', on_delete=models.CASCADE)
#     members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='members_groups', blank=True)

#     def __str__(self):
#         return self.name

  
#     def save(self, *args, **kwargs):
#         if self.pk is not None:  
#             current_members_count = self.members.count()
#             if current_members_count > 6:
#                 raise ValidationError("Members cannot be more than 6.")

#         super().save(*args, **kwargs)


