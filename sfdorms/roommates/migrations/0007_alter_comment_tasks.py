# Generated by Django 5.2 on 2025-05-08 17:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roommates', '0006_rename_task_comment_tasks_alter_task_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='tasks',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='roommates.task'),
        ),
    ]
