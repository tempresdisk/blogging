# Generated by Django 2.2.6 on 2021-01-09 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_auto_20210107_1234'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='follower'),
        ),
    ]
