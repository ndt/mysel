from django.contrib import admin
from django.db import models

class BaseAccountAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.all_objects.all()