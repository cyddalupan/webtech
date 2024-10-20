# Generated by Django 4.2.13 on 2024-10-20 07:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facebook_id', models.CharField(max_length=100, unique=True)),
                ('page_id', models.CharField(max_length=100)),
                ('full_name', models.CharField(max_length=255)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=20, null=True)),
                ('whatsapp_number', models.CharField(blank=True, max_length=20, null=True)),
                ('passport', models.CharField(blank=True, max_length=50, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('reply', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messenger.userprofile')),
            ],
        ),
    ]
