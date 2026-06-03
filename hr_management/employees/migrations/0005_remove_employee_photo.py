from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0004_employee_faculty_employee_graduation_place_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='photo',
        ),
    ]
