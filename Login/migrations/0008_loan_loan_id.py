# Generated by Django 4.2.4 on 2023-08-05 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Login', '0007_alter_monthlyactivity_profit'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='loan_id',
            field=models.IntegerField(default=1),
        ),
    ]
