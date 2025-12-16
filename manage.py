#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import shutil


def clear_media_once():
    # Код виконається тільки в дочірньому процесі реального сервера
    if os.environ.get("RUN_MAIN") == "true":
        MEDIA_DIR = os.path.join(os.path.dirname(__file__), "media")

        if os.path.exists(MEDIA_DIR):
            try:
                shutil.rmtree(MEDIA_DIR)
                os.makedirs(MEDIA_DIR, exist_ok=True)
                print("Папку media очищено перед запуском сервера.")
            except Exception as e:
                print(f"Не вдалося очистити media/: {e}")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    clear_media_once()

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
