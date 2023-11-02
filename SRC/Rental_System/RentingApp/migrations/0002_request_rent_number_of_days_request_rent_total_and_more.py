# Generated by Django 4.2.4 on 2023-09-27 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RentingApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='request_rent',
            name='number_of_days',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='request_rent',
            name='total',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='request_rent',
            name='status',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Pending', 'Pending'), ('Rejected', 'Rejected')], default='Pending', max_length=30),
        ),
    ]