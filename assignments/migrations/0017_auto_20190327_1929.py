# Generated by Django 2.0.4 on 2019-03-27 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0016_auto_20190316_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='simulate',
            field=models.BooleanField(default=False),
        ),
    ]
