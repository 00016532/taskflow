from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .models import Project, Task
from .forms import ProjectForm, TaskForm, RegisterForm


def _sync_project_completion(project):
    total_tasks = project.tasks.count()
    done_tasks = project.tasks.filter(status='done').count()

    if total_tasks > 0 and done_tasks == total_tasks and project.status != 'completed':
        project.status = 'completed'
        project.save(update_fields=['status', 'updated_at'])
    elif project.status == 'completed' and done_tasks < total_tasks:
        project.status = 'active'
        project.save(update_fields=['status', 'updated_at'])


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f'Welcome, {user.username}! Your account was created.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    status_filter = request.GET.get('status', '')
    timeline_projects = Project.objects.filter(owner=request.user)
    if status_filter in ['active', 'completed', 'on_hold']:
        timeline_projects = timeline_projects.filter(status=status_filter)
    timeline_projects = timeline_projects[:6]

    user_tasks = Task.objects.filter(project__owner=request.user)
    recent_tasks = user_tasks.select_related(
        'project').order_by('-created_at')[:5]
    task_stats = user_tasks.aggregate(
        total_tasks=Count('id'),
        done_tasks=Count('id', filter=Q(status='done')),
        in_progress_tasks=Count('id', filter=Q(status='in_progress')),
        todo_tasks=Count('id', filter=Q(status='todo')),
        high_priority=Count('id', filter=Q(priority='high')),
    )

    context = {
        'timeline_projects': timeline_projects,
        'status_filter': status_filter,
        'recent_tasks': recent_tasks,
        **task_stats,
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def project_list(request):
    status_filter = request.GET.get('status', '')
    projects = Project.objects.filter(owner=request.user)

    if status_filter:
        projects = projects.filter(status=status_filter)

    return render(request, 'tasks/project_list.html', {
        'projects': projects,
        'status_filter': status_filter,
    })


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    tasks = project.tasks.all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    return render(request, 'tasks/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'status_filter': status_filter,
    })


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'Project "{project.title}" created!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'tasks/project_form.html',
                  {'form': form, 'action': 'Create'})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'tasks/project_form.html', {
        'form': form, 'action': 'Edit', 'project': project
    })


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        title = project.title
        project.delete()
        messages.success(request, f'Project "{title}" deleted.')
        return redirect('project_list')
    return render(request, 'tasks/project_confirm_delete.html',
                  {'project': project})


@login_required
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            form.save_m2m()
            _sync_project_completion(project)
            messages.success(request, f'Task "{task.title}" created!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {
        'form': form, 'project': project, 'action': 'Create'
    })


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            _sync_project_completion(task.project)
            messages.success(request, 'Task updated!')
            return redirect('project_detail', pk=task.project.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {
        'form': form, 'project': task.project, 'action': 'Edit', 'task': task
    })


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    project = task.project
    project_pk = project.pk
    if request.method == 'POST':
        task.delete()
        _sync_project_completion(project)
        messages.success(request, 'Task deleted.')
        return redirect('project_detail', pk=project_pk)
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_status_update(request, pk):
    """Update task status from project detail form actions."""
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['todo', 'in_progress', 'done']:
            task.status = new_status
            task.save()
            _sync_project_completion(task.project)
            messages.success(
                request, f'Task status updated to "{new_status}".')
    return redirect('project_detail', pk=task.project.pk)


@login_required
def profile(request):
    projects_count = Project.objects.filter(owner=request.user).count()
    tasks_count = Task.objects.filter(project__owner=request.user).count()
    done_count = Task.objects.filter(
        project__owner=request.user,
        status='done').count()
    return render(request, 'tasks/profile.html', {
        'projects_count': projects_count,
        'tasks_count': tasks_count,
        'done_count': done_count,
    })
