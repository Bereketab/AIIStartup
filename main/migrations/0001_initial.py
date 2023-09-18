# Generated by Django 4.2.5 on 2023-09-16 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EthRegion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region_name', models.CharField(choices=[('Addis Ababa', 'Addis Ababa'), ('Afar', 'Afar'), ('Amhara', 'Amhara'), ('Benishangul-Gumuz', 'Benishangul-Gumuz'), ('Dire Dawa', 'Dire Dawa'), ('Gambela', 'Gambela'), ('Harari', 'Harari'), ('Oromia', 'Oromia'), ('Somali', 'Somali'), ('Sidama', 'Sidama '), ('South West Peoples', 'South West'), ('SNNP', 'SNNP'), ('Tigray', 'Tigray')], max_length=50, unique=True, verbose_name='Region')),
            ],
        ),
        migrations.CreateModel(
            name='Wereda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wereda_name', models.CharField(max_length=50, verbose_name='Wereda')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='woredas', to='main.ethregion', verbose_name='Region')),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=50, verbose_name='Country')),
                ('phone_number', models.IntegerField(verbose_name='Phone Number')),
                ('city_name', models.CharField(max_length=50, verbose_name='City Name')),
                ('website', models.CharField(max_length=50, verbose_name='Website')),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='main.wereda', verbose_name='Wereda')),
            ],
        ),
    ]