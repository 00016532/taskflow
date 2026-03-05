import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from tasks.models import Project, Task, Category


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def project(db, user):
    return Project.objects.create(
        title='Test Project',
        description='A test project',
        owner=user,
        status='active'
    )


@pytest.fixture
def category(db):
    return Category.objects.create(name='Backend', color='#007bff')


@pytest.fixture
def task(db, project, category):
    t = Task.objects.create(
        title='Test Task',
        description='A test task',
        project=project,
        priority='high',
        status='todo'
    )
    t.categories.add(category)
    return t


@pytest.mark.django_db
def test_project_creation(project):
    """Test that a project is created with correct fields."""
    assert project.title == 'Test Project'
    assert project.status == 'active'
    assert str(project) == 'Test Project'


@pytest.mark.django_db
def test_task_creation(task):
    """Test that a task is created and linked to a project."""
    assert task.title == 'Test Task'
    assert task.project.title == 'Test Project'
    assert task.priority == 'high'
    assert str(task) == 'Test Task'


@pytest.mark.django_db
def test_category_many_to_many(task, category):
    """Test many-to-many relationship between Task and Category."""
    assert category in task.categories.all()
    assert task in category.tasks.all()


@pytest.mark.django_db
def test_project_progress(project, task):
    """Test project progress calculation."""
    assert project.progress() == 0
    task.status = 'done'
    task.save()
    assert project.progress() == 100


@pytest.mark.django_db
def test_project_progress_is_100_when_project_completed(project):
    """Completed projects should show 100% progress even with no tasks."""
    project.status = 'completed'
    project.save()
    assert project.progress() == 100


@pytest.mark.django_db
def test_project_belongs_to_user(project, user):
    """Test many-to-one: project linked to correct user."""
    assert project.owner == user
    assert project in user.projects.all()


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    """Unauthenticated users should be redirected to login."""
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert '/login/' in response.url


@pytest.mark.django_db
def test_logout_requires_post(client, user):
    """Logout endpoint should reject GET requests."""
    client.login(username='testuser', password='testpass123')
    response = client.get(reverse('logout'))
    assert response.status_code == 405
    assert client.get(reverse('dashboard')).status_code == 200


@pytest.mark.django_db
def test_logout_post_logs_user_out(client, user):
    """POST logout ends the session and redirects to login page."""
    client.login(username='testuser', password='testpass123')
    response = client.post(reverse('logout'))
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert client.get(reverse('dashboard')).status_code == 302


@pytest.mark.django_db
def test_dashboard_authenticated(client, user):
    """Authenticated users can access the dashboard."""
    client.login(username='testuser', password='testpass123')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_high_priority_counts_all_high_tasks(client, user, project):
    """High priority dashboard metric counts high tasks regardless of status."""
    Task.objects.create(title='High To Do', project=project, priority='high', status='todo')
    Task.objects.create(title='High Done', project=project, priority='high', status='done')
    Task.objects.create(title='Medium To Do', project=project, priority='medium', status='todo')

    client.login(username='testuser', password='testpass123')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert response.context['high_priority'] == 2


@pytest.mark.django_db
def test_project_create_view(client, user):
    """Users can create a project via POST."""
    client.login(username='testuser', password='testpass123')
    client.post(reverse('project_create'), {
        'title': 'New Project',
        'description': 'Description',
        'status': 'active',
    })
    assert Project.objects.filter(title='New Project', owner=user).exists()


@pytest.mark.django_db
def test_project_list_only_shows_own(client, db):
    """Users only see their own projects."""
    user1 = User.objects.create_user(username='user1', password='pass123')
    user2 = User.objects.create_user(username='user2', password='pass123')
    Project.objects.create(title='User1 Project', owner=user1, status='active')
    Project.objects.create(title='User2 Project', owner=user2, status='active')

    client.login(username='user1', password='pass123')
    response = client.get(reverse('project_list'))
    assert 'User1 Project' in response.content.decode()
    assert 'User2 Project' not in response.content.decode()


@pytest.mark.django_db
def test_task_delete(client, user, task):
    """Users can delete their own tasks."""
    client.login(username='testuser', password='testpass123')
    task_id = task.pk
    client.post(reverse('task_delete', args=[task_id]))
    assert not Task.objects.filter(pk=task_id).exists()


@pytest.mark.django_db
def test_task_status_update_changes_status(client, user, task):
    """Owner can update task status via POST."""
    client.login(username='testuser', password='testpass123')
    response = client.post(reverse('task_status_update', args=[task.pk]), {'status': 'done'})
    assert response.status_code == 302
    task.refresh_from_db()
    assert task.status == 'done'


@pytest.mark.django_db
def test_task_status_update_rejects_non_owner(client, task):
    """Another user cannot update task status."""
    User.objects.create_user(username='otheruser', password='pass12345')
    client.login(username='otheruser', password='pass12345')
    response = client.post(reverse('task_status_update', args=[task.pk]), {'status': 'done'})
    assert response.status_code == 404
    task.refresh_from_db()
    assert task.status == 'todo'


@pytest.mark.django_db
def test_project_auto_completes_when_all_tasks_done(client, user, project):
    """Project moves to completed when all its tasks are done."""
    t1 = Task.objects.create(title='Task 1', project=project, status='todo')
    t2 = Task.objects.create(title='Task 2', project=project, status='todo')

    client.login(username='testuser', password='testpass123')
    client.post(reverse('task_status_update', args=[t1.pk]), {'status': 'done'})
    project.refresh_from_db()
    assert project.status == 'active'

    client.post(reverse('task_status_update', args=[t2.pk]), {'status': 'done'})
    project.refresh_from_db()
    assert project.status == 'completed'


@pytest.mark.django_db
def test_project_reopens_when_completed_project_gets_open_task(client, user, project):
    """Completed project returns to active if any task becomes non-done."""
    task = Task.objects.create(title='Task 1', project=project, status='done')
    project.status = 'completed'
    project.save()

    client.login(username='testuser', password='testpass123')
    client.post(reverse('task_status_update', args=[task.pk]), {'status': 'todo'})
    project.refresh_from_db()
    assert project.status == 'active'
