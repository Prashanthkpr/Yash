from django import forms
from Projects.models import *
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

class ProjectCreateForm(forms.ModelForm):
    
    class Meta:
        model = Project
        exclude = ('is_active', 'created_by') 
        widgets = {'start_date': NumberInput(attrs={'type':'date'}), 
                   'end_date': NumberInput(attrs={'type':'date'}),
                   'description': SummernoteWidget()
                } 
    def __init__(self, *args, **kwargs):
        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        self.fields['manager'].widget.attrs['required'] = 'required'
        for field in self.fields:
            if field in ['manager', 'team_leader', 'team_members']:
                self.fields[field].widget.attrs['class'] = 'form-control selectpicker'
                self.fields[field].widget.attrs['data-live-search'] = 'true'
                self.fields[field].widget.attrs['data-size'] = '5'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
            if self.fields[field].label:
                required = ''
                if self.fields[field].required:
                    required = '*'
                self.fields[field].widget.attrs['placeholder'] = self.fields[field].label.title()
                self.fields[field].label = f'{self.fields[field].label.title()}{required}'
        self.fields['manager'].label = 'Manager*'

class ProjectDocumentsForm(forms.ModelForm):
    document = forms.FileField(
        widget=forms.FileInput(attrs={'accept': '''application/pdf, application/msword, application/vnd.ms-powerpoint,
            application/vnd.openxmlformats-officedocument.presentationml.slideshow, 
            application/vnd.openxmlformats-officedocument.presentationml.presentation,text/plain'''}),
        required=True,
    )
    class Meta:
        model = ProjectDocuments
        fields = ('name', 'project', 'user', 'description', 'keywords', 'document') 
        widgets = {
                   'description': SummernoteWidget(),
                } 
    def __init__(self, *args, **kwargs):
        super(ProjectDocumentsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if self.fields[field].label:
                required = ''
                if self.fields[field].required:
                    required = '*'
                self.fields[field].widget.attrs['placeholder'] = self.fields[field].label.title()
                self.fields[field].label = f'{self.fields[field].label.title()}{required}'
        self.fields['project'].widget.attrs['disabled'] = True
        self.fields['user'].widget.attrs['disabled'] = True
        self.fields['keywords'].widget.attrs['rows'] = 3
        self.fields['document'].label = "Document*"
        self.fields['document'].help_text = '<i class="color-dimgray">Note: Please upload PDF, DOC and PPT type file.</i>'
        self.fields['keywords'].help_text = '<i class="color-dimgray">Note: Seperate keywords with commas(",").</i>'
    
    def clean_document(self):
        data = self.cleaned_data['document']

        # check if the content type is what we expect
        content_type = data.content_type
        if content_type in ['application/pdf', 'application/msword', 'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain']:
            return data
        else:
            raise ValidationError('Invalid File Type. Please choose valid file.')

