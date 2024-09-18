from django.db import migrations, connection

def create_book_table(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            author VARCHAR(200) NOT NULL,
            genre VARCHAR(50) NOT NULL,
            UNIQUE (title, author, genre)
        );
        """)

def create_review_table(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""       
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            CONSTRAINT unique_user_book_review UNIQUE (book_id, user_id)
        );
        """)

class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunPython(create_book_table),
        migrations.RunPython(create_review_table),
    ]
