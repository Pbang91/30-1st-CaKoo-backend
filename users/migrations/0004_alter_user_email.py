# Generated by Django 4.0.2 on 2022-04-25 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_birthdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'This email has already been registered.'}, max_length=100, unique=True),
        ),
    ]