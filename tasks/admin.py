from django.contrib import admin
from .models import Project, Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'status', 'deadline', 'task_count', 'created_at']
    list_filter = ['status', 'owner']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['priority', 'status', 'project']
    search_fields = ['title', 'description']
    filter_horizontal = ['categories']
