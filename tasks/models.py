from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Task label owned globally and reusable across tasks."""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6c757d')  # hex color
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    """Project container for tasks owned by a single user."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active')
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def task_count(self):
        return self.tasks.count()

    def completed_task_count(self):
        return self.tasks.filter(status='done').count()

    def progress(self):
        if self.status == 'completed':
            return 100
        total = self.task_count()
        if total == 0:
            return 0
        return int((self.completed_task_count() / total) * 100)


class Task(models.Model):
    """Work item inside a project with status, priority, and optional due date."""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks')
    categories = models.ManyToManyField(
        Category, blank=True, related_name='tasks')
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
