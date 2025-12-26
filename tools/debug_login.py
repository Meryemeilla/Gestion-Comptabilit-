
import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'administrateur'
password = 'adminn123'

try:
    user, created = User.objects.get_or_create(username=username)
    user.set_password(password)
    user.role = 'administrateur'
    user.is_staff = True
    user.is_superuser = True
    user.save()
    if created:
        print(f"User '{username}' created with password '{password}'")
    else:
        print(f"User '{username}' updated with password '{password}'")
except Exception as e:
    print(f"Error: {e}")
