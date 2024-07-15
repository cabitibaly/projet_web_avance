from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from teacher.models import Exercice
import secrets

class Student(AbstractUser):
    email = models.EmailField(unique=True)
    phonenumber = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='profile/', default='profile/default-profile.jpg')
    role = models.CharField(max_length=25, default='student')
    point = models.IntegerField(default=0)
    niveau = models.CharField(max_length=25, default='Débutant')

    LEVEL_CHOICES = [
        ('6e', '6e'),
        ('5e', '5e'),
        ('4e', '4e'),
        ('3e', '3e'),
        ('2nde', '2nde'),
        ('1ere', '1ere'),
        ('Tle', 'Tle'),
    ]

    level = models.CharField(max_length=4, choices=LEVEL_CHOICES, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self) -> str:
        return self.email
    
Student._meta.get_field('groups').related_name = 'student_groups'
Student._meta.get_field('user_permissions').related_name = 'student_user_permissions'

class Otp(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, default=secrets.token_hex(3))
    created_at = models.DateTimeField(auto_now=True)
    expire_at = models.DateTimeField(blank=True, null=True)

class Score(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE)
    score = models.CharField(max_length=7)

class Transaction(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    transID = models.CharField(max_length=50, null=False)
    montant = models.IntegerField(default=100)
    status = models.CharField(max_length=20, default="pending")
    token = models.CharField(max_length=255)
