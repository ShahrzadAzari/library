from django.db import migrations, connection

def create_user_table(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(128) NOT NULL
        );
        """)

class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunPython(create_user_table)
    ]
