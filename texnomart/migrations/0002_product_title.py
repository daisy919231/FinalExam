# Generated by Django 5.1.2 on 2024-10-17 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('texnomart', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='title',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
