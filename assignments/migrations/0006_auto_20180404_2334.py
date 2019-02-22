# Generated by Django 2.0.4 on 2018-04-04 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0005_auto_20180404_2100'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='data_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date Updated'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='absolute_path',
            field=models.CharField(editable=False, max_length=200),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='date_created',
            field=models.DateTimeField(auto_created=True, verbose_name='Date Created'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='owner',
            field=models.IntegerField(editable=False),
        ),
    ]
