# Generated by Django 3.1.1 on 2021-08-22 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='title',
            new_name='content',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='qid',
            new_name='questionaire_id',
        ),
        migrations.RemoveField(
            model_name='question',
            name='choise',
        ),
        migrations.RemoveField(
            model_name='question',
            name='must',
        ),
        migrations.AddField(
            model_name='question',
            name='is_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='question',
            name='option',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
