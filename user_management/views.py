from django.contrib.auth.models import User,Group
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404




def user_list(request):
    users = User.objects.all()
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'user_management/user_list.html', {'page_obj': page_obj})


def user_add(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserCreationForm()
    return render(request, 'user_management/user_form.html', {'form': form})



def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'user_management/user_form.html', {'form': form})

def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('user_list')


def group_list(request):
    groups = Group.objects.all()
    return render(request, 'user_management/group_list.html', {'groups': groups})


def group_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        group = Group.objects.create(name=name)
        return redirect('group_list')
    return render(request, 'user_management/group_form.html')

def group_edit(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.name = request.POST.get('name')
        group.save()
        return redirect('group_list')
    return render(request, 'user_management/group_form.html', {'group': group})

def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.delete()
    return redirect('group_list')
