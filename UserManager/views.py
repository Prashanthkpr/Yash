from datetime import datetime
import pdb
from urllib import request
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages #import messages
from django.views import View
from Menu.common import LoginRequiredMixin
from UserManager.models import *
from UserManager.forms import *
from Projects.models import *
from Menu.azure import *
# Create your views here.

class LoginUser(View):
    def get(self, request):
        login_form = UserLoginForm()
        return render(request, 'UserManager/login.html', {'login_form': login_form})
    def post(self, request):
        login_form = UserLoginForm()
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = authenticate(request, email=email, password=password)
        if user_obj is not None:
            login(request, user_obj)
            return redirect('/')
        messages.error(request, "Error, Account not found with the below credentials. Please check the credentials." )
        return render(request, 'UserManager/login.html', {'login_form': login_form})

class RegisterUser(View):
    def get(self, request):
        register_form = UserRegisterForm()
        return render(request, 'UserManager/register.html', {'register_form': register_form})
    def post(self, request):
        register_form = UserRegisterForm(request.POST, request.FILES)
        if register_form.is_valid():
            document_file_obj = request.FILES.get('resume')
            resume_file_name = document_file_obj._name
            resume_uploaded_file_name = f"{datetime.now()}_{document_file_obj._name}"
            container_name = settings.PROJECT_DOCUMENTS_CONTAINER
            document_upload_obj = upload_file_to_azure(
                document_file_obj, container_name, resume_uploaded_file_name
            )
            if document_upload_obj.get('error_code') is None:
                resume_file_size = document_file_obj.size
                resume_file_type = resume_file_name.split('.')[-1]
                resume_file_url = get_file_url(container_name, resume_uploaded_file_name)
                user_obj = register_form.save(commit=False)
                user_obj.resume_file_name = resume_file_name
                user_obj.resume_uploaded_file_name = resume_uploaded_file_name
                user_obj.resume_file_type = resume_file_type
                user_obj.resume_file_size = resume_file_size
                user_obj.resume_file_url = resume_file_url
                user_obj = register_form.save()
                user_obj.set_password(request.POST.get('password'))
                user_obj.username = user_obj.email
                user_obj.save()
                messages.success(request, "User registered successfully." )
                return redirect('/')
            else:
                messages.error(request, "Error, Resume upload failed." )
        messages.error(request, "Error, Please check the errors." )
        return render(request, 'UserManager/register.html', {'register_form': register_form, 'failure': True})


class UserLogout(View):
    def get(self, request):
        logout(request)
        return redirect('/')
    

class UsersList(LoginRequiredMixin, View):
    
    def get(self, request):
        users = []
        user = request.user
        if user.is_superuser:
            users = User.objects.all()
        else:
            projects = Project.objects.filter(Q(manager=user)|Q(team_leader=user)|Q(created_by=user)|Q(team_members=user))
            managers = list(projects.filter(manager__isnull=False).values_list('manager', flat=True))
            team_leaders = list(projects.filter(team_leader__isnull=False).values_list('team_leader', flat=True))
            user_ids = managers
            user_ids.extend(team_leaders)
            for project in projects:
                user_ids.extend(project.team_members.values_list('id', flat=True))
            user_ids = list(set(user_ids))
            users = User.objects.filter(id__in=user_ids)
        return render(request, 'UserManager/users_list.html', {'users': users})


class UsersUpdate(LoginRequiredMixin, View):
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            user_update_form = UserUpdateForm(instance=user)
            user_password_reset_form = UserPasswordResetForm(instance=user)
            return render(request, 'UserManager/user_update.html', 
                {'user_update_form': user_update_form, 'user_password_reset_form': user_password_reset_form, 'user': user})
        raise Http404("Page not found.")
    
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            user_update_form = UserUpdateForm(request.POST, instance=user)
            if user_update_form.is_valid():
                user_obj = user_update_form.save()
                document_file_obj = request.FILES.get('resume')
                if document_file_obj:
                    resume_file_name = document_file_obj._name
                    resume_uploaded_file_name = f"{datetime.now()}_{document_file_obj._name}"
                    container_name = settings.PROJECT_DOCUMENTS_CONTAINER
                    document_upload_obj = upload_file_to_azure(
                        document_file_obj, container_name, resume_uploaded_file_name
                    )
                    if document_upload_obj.get('error_code') is None:
                        resume_file_size = document_file_obj.size
                        resume_file_type = resume_file_name.split('.')[-1]
                        resume_file_url = get_file_url(container_name, resume_uploaded_file_name)
                        user_obj.resume_file_name = resume_file_name
                        user_obj.resume_uploaded_file_name = resume_uploaded_file_name
                        user_obj.resume_file_type = resume_file_type
                        user_obj.resume_file_size = resume_file_size
                        user_obj.resume_file_url = resume_file_url
                        user_obj.save()
                messages.success(request, 'User updated successfully.')
                return redirect('.')
            messages.error(request, 'Please check the errors.')
            return render(request, 'UserManager/user_update.html', {'user_update_form': user_update_form})
        raise Http404("Page not found.")


class UsersPasswordReset(LoginRequiredMixin, View):
    
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            user_update_form = UserUpdateForm(instance=user)
            user_password_reset_form = UserPasswordResetForm(request.POST, instance=user)
            if user_password_reset_form.is_valid():
                password = request.POST.get('password')
                messages.success(request, 'User Password reset successfully.')
                return redirect(reverse('UserManager:users-update', args=[user.id]))
            messages.error(request, 'Please check the errors.')
            return render(request, 'UserManager/user_update.html', 
                {'user_update_form': user_update_form, 'user_password_reset_form': user_password_reset_form})
        raise Http404("Page not found.")