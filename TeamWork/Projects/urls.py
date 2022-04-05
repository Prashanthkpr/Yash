from django.urls import path
from Projects.views import *
app_name = 'Projects'

urlpatterns = [
    path('', ProjectsHome.as_view(), name="home"),
    path('create/', ProjectsCreate.as_view(), name="create"),
    path('update/<int:project_id>/', ProjectsUpdate.as_view(), name="update"),
    path('details/<int:project_id>/', ProjectsDetails.as_view(), name="details"),
    path('delete/<int:project_id>/', ProjectDelete.as_view(), name="delete"),
    path('<int:project_id>/documents/upload/', ProjectDocumentsCreate.as_view(),
         name="project-documents-upload"),
    path('<int:project_id>/documents/upload/<int:document_id>/update/',
          ProjectDocumentsUploadUpdate.as_view(),
         name="project-documents-upload-update"),
    path('<int:project_id>/documents/upload/<int:document_id>/details/',
          ProjectDocumentsUploadDetails.as_view(),
         name="project-documents-upload-details"),
    path('<int:project_id>/documents/upload/<int:document_id>/delete/',
          ProjectDocumentsUploadDelete.as_view(),
         name="project-documents-upload-delete"),
    path('<int:project_id>/documents/', ProjectDocumentsListIndex.as_view(),
         name="project-documents-list-index"),
    path('<int:project_id>/documents/list/', ProjectDocumentsList.as_view(),
         name="project-documents-list"),
    path('documents/', DocumentsListIndex.as_view(),
         name="documents-list-index"),
    path('documents/list/', DocumentsList.as_view(),
         name="documents-list"),
]
