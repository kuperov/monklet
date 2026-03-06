from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0002_alter_enquiry_options_enquiry_message_enquiry_name"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Enquiry",
        ),
    ]

