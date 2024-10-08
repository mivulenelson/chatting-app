from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.dispatch import receiver
from django.db.models import Max
from django.db.models.functions import Cast, Substr
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError


class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("User must have a username.")
        if not email:
            raise ValueError("User must have an email address.")
        #if not email.endswith("@gmail.com"):
         #   raise ValueError("Email must be a Gmail.")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields,
        )

        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def update_user(self, user_id, email, **extra_fields):
        email = self.normalize_username(email)
        if self.model.objects.filter(email=email).exclude(id=user_id).exists():
            raise ValueError("A user with this email already exists.")
        user = self.get(id=user_id)
        user.email = email
        for key, value in extra_fields.items():
            setattr(user, key, value)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=30, unique=True, primary_key=True)
    username = models.CharField(max_length=100, unique=True, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ("email",)

    def __str__(self):
        return self.username

    '''
    def clean(self):
        super().clean()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', self.email):
            raise ValidationError("Email must be a valid Gmail address.")
    '''

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    '''
    @property
    def is_staff(self):
        return self.is_admin
    '''
    def send_user_id_email(self):
        subject = f"{self.email}"
        message = f"""
        Hello {self.username}: {self.user_id},
        Thank you for registering!
        
        Here are your details:
        User ID: {self.user_id}
        Email: {self.email}
        
        Please keep this information safe
        
        Best regards,
        From Chatapp
        """
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = (self.email,)
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)


# Creating custom user ID
@receiver(pre_save, sender=CustomUser)
def generate_user_id(sender, instance, **kwargs, ):
    if not instance.user_id:
        date_user_joined = instance.created_at or datetime.now()
        date_to_string = date_user_joined.strftime('%d%m%Y')

        maximum_id_dictionary = CustomUser.objects.filter(user_id__startswith=f"USER - {date_to_string} -").aggregate(
            maximum_id = Max(
                Cast(
                    Substr("user_id",len(f"USER - {date_to_string} - ") + 1),
                    output_field=models.IntegerField(),
                )
            )
        )
        maximum_id = maximum_id_dictionary["maximum_id"] if maximum_id_dictionary["maximum_id"] is not None else 0

        new_user_id = maximum_id + 1
        instance.user_id = f"USER - {date_to_string} - {new_user_id}"
