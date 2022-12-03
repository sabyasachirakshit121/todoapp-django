import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords


class CustomUser(AbstractUser):
    # gender choices
    GENDER_NA = 0
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER = ((GENDER_NA, 'Not Available'),
              (GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female'))

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4(), editable=False)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=255, unique=False)
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(
        max_length=255, unique=True, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    gender = models.IntegerField(choices=GENDER, default=GENDER_NA)
    email_confirmed = models.BooleanField(default=False)
    history = HistoricalRecords()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        self.username = f"{self.first_name}-{self.last_name}"
        super(CustomUser, self).save(*args, **kwargs)
