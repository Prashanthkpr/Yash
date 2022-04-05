from pydoc import describe
from django.db import models
from Menu.models import TeamWorkAbstractModel
# Create your models here.

class Project(TeamWorkAbstractModel):
    name = models.CharField(max_length=128, unique=True)
    project_id = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'UserManager.User', related_name="prject_created_by",
        on_delete=models.SET_NULL, null=True, blank=True
    )
    manager = models.ForeignKey(
        'UserManager.User', related_name="prject_manager",
        on_delete=models.SET_NULL, null=True, blank=True
    )
    team_leader = models.ForeignKey(
        'UserManager.User', related_name="prject_team_leader",
        on_delete=models.SET_NULL, null=True, blank=True
    )
    team_members = models.ManyToManyField('UserManager.User', blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    def __str__(self) -> str:
        return self.name
    

class ProjectDocuments(TeamWorkAbstractModel):
    name = models.CharField(max_length=128, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey('UserManager.User', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=512)
    uploaded_file_name = models.CharField(max_length=512, null=True)
    file_type = models.CharField(max_length=10)
    file_size = models.PositiveIntegerField()
    file_url = models.TextField()
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    
    def __str__(self) -> str:
        return self.name
    