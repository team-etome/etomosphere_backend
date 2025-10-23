from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from storages.backends.s3boto3 import S3Boto3Storage




class God(AbstractUser):
    user_name      = models.CharField(max_length=50,unique=True)
    email          = models.EmailField(unique=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name           ='groups',
        blank                  =True,
        help_text              ='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name           ="god_user_set",
        related_query_name     ="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name             ='user permissions',
        blank                    =True,
        help_text                ='Specific permissions for this user.',
        related_name             ="god_user_set",
        related_query_name       ="user",
    )



    objects = UserManager()
    USERNAME_FIELD       = 'email'
    REQUIRED_FIELDS      =[]

    def __str__(self):
        return self.email





class User(AbstractUser):
    """Extended User model for Etomosphere"""
    
    # Custom fields for sign-up form
    first_name               = models.CharField(max_length=100, blank=True, null=True)
    email                    = models.EmailField(unique=True)
    password                 = models.CharField(max_length=100, blank=True, null=True)
    phone                    = models.CharField(max_length=15, blank=True, null=True)
    created_at               = models.DateTimeField(auto_now_add=True)
    updated_at               = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if hasattr(self, 'email') and self.email:
            self.email = self.email.lower()
        super(User, self).save(*args, **kwargs)
