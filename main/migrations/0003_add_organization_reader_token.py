from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0002_rename_organizer_organization_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='reader_token',
            field=models.CharField(max_length=64, blank=True, null=True, unique=True),
        ),
    ]
