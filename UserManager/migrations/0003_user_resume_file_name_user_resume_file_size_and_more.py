# Generated by Django 4.0.3 on 2022-04-11 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserManager', '0002_alter_user_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='resume_file_name',
            field=models.CharField(max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='resume_file_size',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='user',
            name='resume_file_type',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='resume_file_url',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='resume_uploaded_file_name',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'A user with that email address already exists.'}, help_text='Please provide Yash Email.', max_length=254, unique=True, verbose_name='email address'),
        ),
    ]
