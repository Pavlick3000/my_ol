# Generated by Django 5.0 on 2024-09-06 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NomencBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(db_collation='Cyrillic_General_CI_AS', db_column='_Description', max_length=100)),
            ],
            options={
                'db_table': '_Reference175',
                'managed': False,
            },
        ),
    ]
