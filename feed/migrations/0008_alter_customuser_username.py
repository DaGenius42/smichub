# Shorten the username max length from 150 to 20 characters.

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0007_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(
                error_messages={'unique': 'A user with that username already exists.'},
                help_text='Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only.',
                max_length=20,
                unique=True,
                validators=[UnicodeUsernameValidator()],
                verbose_name='username',
            ),
        ),
    ]
