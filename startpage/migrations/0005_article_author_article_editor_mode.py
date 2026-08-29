# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('startpage', '0004_activesession_sitesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='editor_mode',
            field=models.CharField(
                choices=[('legacy', 'Legacy'), ('modern', 'Modern')],
                default='legacy',
                help_text="'legacy' uses plain text rendering; 'modern' renders rich HTML content",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='articles',
                to='auth.user',
            ),
        ),
    ]
