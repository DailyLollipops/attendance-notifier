# Generated by Django 4.2.5 on 2023-09-17 08:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('students', models.ManyToManyField(to='core.student')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.teacher')),
            ],
        ),
    ]
