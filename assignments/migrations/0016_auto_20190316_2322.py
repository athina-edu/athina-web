# Generated by Django 2.0.4 on 2019-03-16 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0015_auto_20190307_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='git_password',
            field=models.CharField(blank=True, default='', help_text='Use an access token and not your real password.', max_length=255),
        ),
    ]
