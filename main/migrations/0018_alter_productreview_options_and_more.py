# Generated by Django 4.0.4 on 2022-07-27 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_alter_productreview_options_alter_wishlist_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productreview',
            options={'verbose_name_plural': 'Reviews'},
        ),
        migrations.AlterModelOptions(
            name='useraddressbook',
            options={'verbose_name_plural': 'AddressBook'},
        ),
        migrations.AlterModelOptions(
            name='wishlist',
            options={'verbose_name_plural': 'Wishlist'},
        ),
    ]