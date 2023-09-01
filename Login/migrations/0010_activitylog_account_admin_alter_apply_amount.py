# Generated by Django 4.2.4 on 2023-08-15 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Login', '0009_alter_apply_member_alter_contribution_member_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=20)),
                ('action', models.CharField(max_length=200)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('details', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='admin',
            field=models.BooleanField(default=0),
        ),
        migrations.AlterField(
            model_name='apply',
            name='amount',
            field=models.DecimalField(decimal_places=1, max_digits=10),
        ),
    ]