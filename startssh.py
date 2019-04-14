import os
import sys

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "autops.settings")
    import django
    django.setup()

    from backend import main


    interactice_obj = main.ArgvHandler(sys.argv)
    interactice_obj.run()

