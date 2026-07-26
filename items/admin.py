from django.contrib import admin
from .models import LostItem, FoundItem

admin.site.register(LostItem)
admin.site.register(FoundItem)