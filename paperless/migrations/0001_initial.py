# Generated by Django 4.2 on 2023-06-26 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Facture",
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
                ("location", models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("siret", models.BigIntegerField(primary_key=True, serialize=False)),
                ("nom", models.CharField(max_length=128)),
                ("password", models.CharField(max_length=258)),
                ("factures", models.ManyToManyField(to="paperless.facture")),
            ],
        ),
    ]