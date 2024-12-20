# Generated by Django 5.1.2 on 2024-10-31 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FacebookPage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("page_id", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("details", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Facebook Page",
                "verbose_name_plural": "Facebook Pages",
            },
        ),
    ]
