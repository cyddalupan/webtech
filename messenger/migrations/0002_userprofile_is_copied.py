# Generated by Django 4.2.16 on 2024-10-25 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_copied',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
