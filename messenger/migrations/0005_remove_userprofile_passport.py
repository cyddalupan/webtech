# Generated by Django 5.1.2 on 2024-11-05 05:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("messenger", "0004_alter_userprofile_age"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userprofile",
            name="passport",
        ),
    ]
