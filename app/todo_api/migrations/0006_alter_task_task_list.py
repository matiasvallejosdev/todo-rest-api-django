# Generated by Django 4.0 on 2023-04-20 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('todo_api', '0005_alter_task_task_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_list',
            field=models.ForeignKey(blank=True, default='inbox', null=True, on_delete=django.db.models.deletion.CASCADE, to='todo_api.tasklist'),
        ),
    ]