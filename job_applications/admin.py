from django.contrib import admin

from .models import Application, Job


@admin.register(Application)
class ApplicationModelAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "job", "status", "applied_date"]
    list_filter = ["status", "applied_date", "job"]
    search_fields = ["name", "email", "phone"]


@admin.register(Job)
class JobModelAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "dept", "location", "job_type"]
    search_fields = ["title", "dept", "location"]
