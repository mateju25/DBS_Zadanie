# Generated by Django 3.1.6 on 2021-04-28 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('v2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulletinissues',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='orpodanieissues',
            name='bulletin_issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='v2.bulletinissues'),
        ),
        migrations.AlterField(
            model_name='orpodanieissues',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='orpodanieissues',
            name='raw_issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='v2.rawissues'),
        ),
        migrations.AlterField(
            model_name='rawissues',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
