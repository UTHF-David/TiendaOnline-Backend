# Generated by Django 5.2 on 2025-05-22 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TiendaOnline', '0007_alter_usuario_pais'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='pais',
            field=models.CharField(max_length=100, null=True, verbose_name='País'),
        ),
        migrations.DeleteModel(
            name='ISVPais',
        ),
    ]
