from ast import keyword
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import *
from django.contrib import messages #import messages
from django.views import View
from Menu.common import LoginRequiredMixin
from Projects.models import *
from UserManager.models import User
from Projects.forms import *
from Menu.azure import *
from django.conf import settings
# Create your views here.

class ProjectsHome(LoginRequiredMixin, View):
    
    def get(self, request):
        projects = Project.objects.all()
        user = request.user
        if not user.is_superuser:
            projects = projects.filter(Q(manager=user)|Q(team_leader=user)|Q(created_by=user)|Q(team_members=user))
        return render(request, 'Projects/home.html', {'projects': projects.distinct()})


class ProjectsCreate(LoginRequiredMixin, View):
    
    def get(self, request):
        project_create_form = ProjectCreateForm()
        return render(request, 'Projects/create.html', {'project_create_form': project_create_form})
    
    def post(self, request):
        project_create_form = ProjectCreateForm(request.POST)
        if project_create_form.is_valid():
            project_obj = project_create_form.save(commit=False)
            project_obj.created_by = request.user
            project_obj.save()
            project_obj.team_members.add(*request.POST.getlist('team_members'))
            messages.success(request, "Project created successfully." )
            return redirect('/')
        messages.error(request, "Error, Please check the errors." )
        return render(request, 'Projects/create.html', {'project_create_form': project_create_form})
    

class ProjectsUpdate(LoginRequiredMixin, View):
    
    def get(self, request, project_id):
        project_obj = get_object_or_404(Project, id=project_id)
        project_update_form = ProjectCreateForm(instance=project_obj)
        return render(request, 'Projects/update.html', {'project_update_form': project_update_form})
    
    def post(self, request, project_id):
        project_obj = get_object_or_404(Project, id=project_id)
        project_update_form = ProjectCreateForm(request.POST, instance=project_obj)
        if project_update_form.is_valid():
            project_obj = project_update_form.save()
            project_obj.team_members.clear()
            project_obj.team_members.add(*request.POST.getlist('team_members'))
            messages.success(request, "Project updated successfully." )
            return redirect('.')
        messages.error(request, "Error, Please check the errors." )
        return render(request, 'Projects/update.html', {'project_update_form': project_update_form})

class ProjectsDetails(LoginRequiredMixin, View):
    
    def get(self, request, project_id):
        project_obj = get_object_or_404(Project, id=project_id)
        return render(request, 'Projects/details.html', {'project_obj': project_obj})

class ProjectDelete(LoginRequiredMixin, View):
    
    def get(self, request, project_id):
        project_obj = get_object_or_404(Project, id=project_id)
        if request.user.is_superuser or project_obj.manager == request.user:
            try:
                project_obj.delete()
                messages.success(request, "Project deleted successfully." )
            except Exception as e:
                print(e)
                messages.error(request, "Error, Please check the errors." )
                return JsonResponse({'success': False})
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    


class ProjectDocumentsCreate(LoginRequiredMixin, View):
    
    def get(self, request, project_id):
        project_obj = get_object_or_404(Project, id=project_id)
        initial = {'project': project_obj, 'user': request.user}
        project_documents_form = ProjectDocumentsForm(initial=initial)
        return render(
            request, 'Projects/project_documents_create.html',
            {'project_document_form': project_documents_form, 'project_obj': project_obj}
        )
    
    def post(self, request, project_id):
        project_obj = get_object_or_404(Project, id=project_id)
        initial = {'project': project_obj, 'user': request.user}
        data = request.POST.copy()
        data['project'] = project_obj.id
        data['user'] = request.user.id
        project_documents_form = ProjectDocumentsForm(data, request.FILES, initial=initial)
        if project_documents_form.is_valid():
            document_file_obj = request.FILES.get('document')
            file_name = document_file_obj._name
            uploaded_file_name = f"{datetime.now()}_{document_file_obj._name}"
            container_name = settings.PROJECT_DOCUMENTS_CONTAINER
            document_upload_obj = upload_file_to_azure(
                document_file_obj, container_name, uploaded_file_name
            )
            if document_upload_obj.get('error_code') is None:
                file_size = document_file_obj.size
                file_type = file_name.split('.')[-1]
                file_url = get_file_url(container_name, uploaded_file_name)
                project_document = project_documents_form.save(commit=False)
                project_document.user = request.user
                project_document.project = project_obj
                project_document.is_active = True
                project_document.file_name = file_name
                project_document.uploaded_file_name = uploaded_file_name
                project_document.file_size = file_size
                project_document.file_url = file_url
                project_document.file_type = file_type
                project_document.save()
                messages.success(request, "Document uploaded successfully." )
                return redirect(reverse('Projects:project-documents-list-index', args=[project_id]))
            else:
                messages.error(request, f"Error, {document_upload_obj.get('error_code')}" )
        else:
            messages.error(request, "Error, Please check the errors." )
        return render(
            request, 'Projects/project_documents_create.html',
            {'project_document_form': project_documents_form, 'project_obj': project_obj}
        )
        

class ProjectDocumentsListIndex(LoginRequiredMixin, View):
    
    def get(self, request, project_id):
        project_obj = get_object_or_404(Project, id=project_id)
        project_documents = ProjectDocuments.objects.filter(project=project_obj)
        uploaded_users = User.objects.filter(id__in=project_documents.values_list('user', flat=True))
        start_date = project_documents.aggregate(start_date=Min('created_at')).get('start_date')
        end_date = project_documents.aggregate(end_date=Max('created_at')).get('end_date')
        filters = {
            'names': project_documents.values_list('name', flat=True),
            'file_names': project_documents.values_list('file_name', flat=True),
            'uploaded_users': uploaded_users, 'start_date': start_date, 'end_date': end_date
        }
        return render(
            request, 'Projects/project_documents_list_index.html', 
                { 'project_obj': project_obj, 'filters': filters}
        )

def filter_documents(project_documents, request):
    search_term = request.GET.get('search_term')
    if search_term:
        project_documents = project_documents.filter(
            Q(keywords__icontains=search_term) | Q(name__icontains=search_term) |
            Q(file_name__icontains=search_term) | Q(description__icontains=search_term)
        )
    name = request.GET.get('name')
    if name:
        project_documents = project_documents.filter(name=name)
    project = request.GET.get('project')
    if project:
        project_documents = project_documents.filter(project_id=project)
    user = request.GET.get('user')
    if user:
        project_documents = project_documents.filter(user_id=user)
    file_name = request.GET.get('file_name')
    if file_name:
        project_documents = project_documents.filter(file_name=file_name)
    file_type = request.GET.get('file_type')
    if file_type:
        project_documents = project_documents.filter(file_type__in=file_type.split(','))
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        project_documents = project_documents.filter(created_at__date__gte=start_date)
    if end_date:
        project_documents = project_documents.filter(created_at__date__lte=end_date)   
    return project_documents        

class ProjectDocumentsList(LoginRequiredMixin, View):
    
    def get(self, request, project_id):
        project_obj = get_object_or_404(Project, id=project_id)
        project_documents = ProjectDocuments.objects.filter(project=project_obj)
        project_documents = filter_documents(project_documents, request)
        return render(
            request, 'Projects/project_documents_list.html',
            {'project_documents': project_documents.order_by('-id'), 'project_obj': project_obj}
        )
        

class ProjectDocumentsUploadUpdate(LoginRequiredMixin, View):
    
    def get(self, request, project_id, document_id):
        project_obj = get_object_or_404(Project, id=project_id)
        document_obj = get_object_or_404(ProjectDocuments, id=document_id)
        if document_obj.project == project_obj:
            initial = {'project': project_obj, 'user': request.user}
            project_documents_form = ProjectDocumentsForm(instance=document_obj)
            return render(
                request, 'Projects/project_documents_update.html',
                {'project_document_form': project_documents_form, 'project_obj': project_obj}
            )
        messages.error('Error, Something went wrong.')
        return redirect('/')
    
    def post(self, request, project_id, document_id):
        project_obj = get_object_or_404(Project, id=project_id)
        document_obj = get_object_or_404(ProjectDocuments, id=document_id)
        data = request.POST.copy()
        data['project'] = project_obj.id
        data['user'] = request.user.id
        project_documents_form = ProjectDocumentsForm(data, request.FILES, instance=document_obj)
        if project_documents_form.is_valid():
            project_document = project_documents_form.save()
            document_file_obj = request.FILES.get('document')
            if document_file_obj:
                file_name = document_file_obj._name
                uploaded_file_name = f"{datetime.now()}_{document_file_obj._name}"
                container_name = settings.PROJECT_DOCUMENTS_CONTAINER
                document_upload_obj = upload_file_to_azure(
                    document_file_obj, container_name, uploaded_file_name
                )
                if document_upload_obj.get('error_code') is None:
                    file_size = document_file_obj.size
                    file_type = file_name.split('.')[-1]
                    file_url = get_file_url(container_name, uploaded_file_name)
                    project_document.user = request.user
                    project_document.project = project_obj
                    project_document.is_active = True
                    project_document.file_name = file_name
                    project_document.uploaded_file_name = uploaded_file_name
                    project_document.file_size = file_size
                    project_document.file_url = file_url
                    project_document.file_type = file_type
                    project_document.save()
                else:
                    messages.error(request, f"Error, {document_upload_obj.get('error_code')}" )
            messages.success(request, "Document updated successfully." )
            return redirect(reverse('Projects:project-documents-upload-update', args=[project_id, document_id]))
        else:
            messages.error(request, "Error, Please check the errors." )
        return render(
            request, 'Projects/project_documents_create.html',
            {'project_document_form': project_documents_form, 'project_obj': project_obj}
        )

class ProjectDocumentsUploadDetails(LoginRequiredMixin, View):
    
    def get(self, request, project_id, document_id):
        project_obj = get_object_or_404(Project, id=project_id)
        document_obj = get_object_or_404(ProjectDocuments, id=document_id)
        if document_obj.project == project_obj:
            initial = {'project': project_obj, 'user': request.user}
            project_documents_form = ProjectDocumentsForm(instance=document_obj)
            return render(
                request, 'Projects/project_documents_details.html',
                {'project_document_form': project_documents_form, 'project_obj': project_obj}
            )
        messages.error('Error, Something went wrong.')
        return redirect('/')
            

class ProjectDocumentsUploadDelete(LoginRequiredMixin, View):
    
    def get(self, request, project_id, document_id):
        document_obj = get_object_or_404(ProjectDocuments, id=document_id)
        if document_obj.user == request.user:
            try:
                document_obj.delete()
                messages.success(request, "Document deleted successfully." )
            except Exception as e:
                print(e)
                messages.error(request, "Error, Please check the errors." )
                return JsonResponse({'success': False})
            return JsonResponse({'success': True})
        messages.error(request, "Error, Please check the errors." )
        return JsonResponse({'success': False})
        
        
class DocumentsListIndex(LoginRequiredMixin, View):
    
    def get(self, request):
        user = request.user
        projects = Project.objects.filter(Q(manager=user)|Q(team_leader=user)|Q(created_by=user)|Q(team_members=user))
        project_documents = ProjectDocuments.objects.filter(project__in=projects)
        uploaded_users = User.objects.filter(id__in=project_documents.values_list('user', flat=True))
        start_date = project_documents.aggregate(start_date=Min('created_at')).get('start_date')
        end_date = project_documents.aggregate(end_date=Max('created_at')).get('end_date')
        filters = {
            'names': project_documents.values_list('name', flat=True),
            'projects': projects,
            'file_names': project_documents.values_list('file_name', flat=True),
            'uploaded_users': uploaded_users, 'start_date': start_date, 'end_date': end_date
        }
        return render(
            request, 'Projects/documents/documents_list_index.html', {'filters': filters}
        )
        

class DocumentsList(LoginRequiredMixin, View):
    
    def get(self, request):
        user = request.user
        projects = Project.objects.filter(Q(manager=user)|Q(team_leader=user)|Q(created_by=user)|Q(team_members=user))
        project_documents = ProjectDocuments.objects.filter(project__in=projects)
        project_documents = filter_documents(project_documents, request)
        return render(
            request, 'Projects/documents/documents_list.html',
            {'project_documents': project_documents.order_by('-id')}
        )