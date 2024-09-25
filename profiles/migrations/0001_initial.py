# Generated by Django 5.1.1 on 2024-09-25 09:08

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Profile",
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
                ("bio", models.TextField(blank=True, default="")),
                ("link_1", models.URLField(blank=True, default="")),
                ("link_2", models.URLField(blank=True, default="")),
                (
                    "profile_image",
                    models.URLField(blank=True, default="", max_length=300),
                ),
            ],
        ),
    ]
