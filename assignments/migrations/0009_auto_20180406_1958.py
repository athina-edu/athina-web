# Generated by Django 2.0.4 on 2018-04-06 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0008_auto_20180404_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='id',
            field=models.IntegerField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]
