from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = [('student', 'Student'), ('admin_user', 'Admin')]
    role = models.CharField(max_length=20, choices=ROLES, default='student')
    phone_number = models.CharField(max_length=20, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_set',
        blank=True
    )

    def is_admin_user(self):
        return self.role == 'admin_user'