# Generated by Django 4.2.16 on 2024-11-01 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0003_alter_userprofile_is_copied'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='age',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
