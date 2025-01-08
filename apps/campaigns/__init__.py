from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='EmailCampaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('recipients', models.TextField()),
                ('status', models.CharField(choices=[('Draft', 'Draft'), ('Scheduled', 'Scheduled'), ('Sent', 'Sent')], default='Draft', max_length=10)),
                ('schedule_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        # Other model creations...
    ]
