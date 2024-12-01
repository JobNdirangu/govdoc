from django.contrib.auth.models import User,Group
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from management.models import Ministry,Department
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib import messages


@login_required
def dashboard_users(request):
    if not request.user.is_superuser:  
        return redirect('login')
    user_count = User.objects.count()
    group_count = Group.objects.count()

    context = {
        'user_count': user_count,
        'group_count': group_count,
    }
    return render(request, 'user_management/dashboard.html', context)


def manage_inactive_users(request):
    if not request.user.is_superuser:  
        return redirect('login')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            messages.success(request, f"User {user.username} has been activated.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    inactive_users = User.objects.filter(is_active=False)
    paginator = Paginator(inactive_users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for index, inactive_users in enumerate(page_obj.object_list):
        inactive_users.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page

    return render(request, 'user_management/manage_inactive_users.html', {'page_obj': page_obj})


@login_required
def user_list(request):
    if not request.user.is_superuser:  
        return redirect('login')
    users = User.objects.all()
    paginator = Paginator(users, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'user_management/user_list.html', {'page_obj': page_obj})

@login_required
def user_add(request):
    if not request.user.is_superuser:  
        return redirect('login')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, 'user_management/user_form.html', {'form': form})

@login_required
def user_edit(request, pk):
    if not request.user.is_superuser:  
        return redirect('login')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'user_management/user_form.html', {'form': form})

@login_required
def user_delete(request, pk):
    if not request.user.is_superuser:  
        return redirect('login')
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('user_list')

@login_required
def group_list(request):
    if not request.user.is_superuser:  
        return redirect('login')
    groups = Group.objects.all()
    return render(request, 'user_management/group_list.html', {'groups': groups})

@login_required
def group_add(request):
    if not request.user.is_superuser:  
        return redirect('login')
    if request.method == 'POST':
        name = request.POST.get('name')
        Group.objects.create(name=name)
        return redirect('group_list')

@login_required
def group_edit(request, pk):
    if not request.user.is_superuser:  
        return redirect('login')
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.name = request.POST.get('name')
        group.save()
        return redirect('group_list')

@login_required
def group_delete(request, pk):
    if not request.user.is_superuser:  
        return redirect('login')
    group = get_object_or_404(Group, pk=pk)
    group.delete()
    return redirect('group_list')


# Ministry Views
@login_required
def ministry_list_create(request):
    if not request.user.is_superuser:  
        return redirect('login')
    if request.method == 'POST':  
        name = request.POST['name']
        description = request.POST.get('description', '')
        Ministry.objects.create(name=name, description=description)
        messages.success(request, f'{name}, have been created successfully')

        return redirect('ministry_list_create')
    
    ministries = Ministry.objects.all()
    paginator = Paginator(ministries, 1)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for index, documents in enumerate(page_obj.object_list):
        documents.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page

    return render(request, 'user_management/ministry_list_create.html', {'page_obj': page_obj})


@login_required
def ministry_edit(request, pk):
    if not request.user.is_superuser:  
        return redirect('login')
    ministry = get_object_or_404(Ministry, pk=pk)
    if request.method == 'POST':  
        ministry.name = request.POST['name']
        ministry.description = request.POST.get('description', '')
        ministry.save()
        messages.success(request, f'{ministry.name}, have been updated successfully')
        return redirect('ministry_list_create')

    return redirect('ministry_list_create')

def ministry_delete(request, pk):
    if not request.user.is_superuser:  
        return redirect('login')
    ministry = get_object_or_404(Ministry, pk=pk)
    ministry.delete()
    messages.success(request, f'{ministry.name}, have been deleted successfully')
    return redirect('ministry_list_create')


# Department Views
def department_list_create(request):
    if not request.user.is_superuser:  
        return redirect('login')
    
    if request.method == 'POST':  
        name = request.POST['name']
        description = request.POST.get('description', '')
        ministry_id = request.POST['ministry']
        ministry = get_object_or_404(Ministry, pk=ministry_id)
        Department.objects.create(name=name, description=description, ministry=ministry)
        messages.success(request, f'{name}, have been created successfully')

        return redirect('department_list_create')
    else:
        departments = Department.objects.select_related('ministry').all()
        ministries = Ministry.objects.all()
        paginator = Paginator(departments, 10)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        for index, documents in enumerate(page_obj.object_list):
            documents.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page

    return render(request, 'user_management/department_list_create.html', {
        'page_obj': page_obj,
        'ministries': ministries
    })


def department_edit(request, pk):
    if not request.user.is_superuser:  
        return redirect('login')
    department = get_object_or_404(Department, pk=pk)
    ministries = Ministry.objects.all()

    if request.method == 'POST':  
        department.name = request.POST['name']
        department.description = request.POST.get('description', '')
        ministry_id = request.POST['ministry']
        department.ministry = get_object_or_404(Ministry, pk=ministry_id)
        department.save()
        messages.success(request, f'{department.name}, have been updated successfully')

        return redirect('department_list_create')

    return render(request, 'user_management/department_edit.html', {
        'department': department,
        'ministries': ministries
    })


def department_delete(request, pk):
    if not request.user.is_superuser:  
        return redirect('login')
    department = get_object_or_404(Department, pk=pk)
    department.delete()
    messages.success(request, f'{department.name}, have been deleted successfully')

    return redirect('department_list_create')


