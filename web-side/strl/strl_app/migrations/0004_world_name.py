# Generated by Django 2.0.6 on 2018-07-13 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strl_app', '0003_auto_20180709_0919'),
    ]

    operations = [
        migrations.AddField(
            model_name='world',
            name='name',
            field=models.CharField(default='World', max_length=50),
        ),
    ]
