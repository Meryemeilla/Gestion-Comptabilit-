
import os
import sys
import django
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from utilisateurs.views import role_based_redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def test_fix():
    print("Testing role_based_redirect fix...")
    
    # Mock request and user
    request = MagicMock()
    request.user.is_authenticated = True
    
    user = MagicMock()
    user.username = 'testuser'
    user.is_superuser = False
    user.is_administrateur = False
    # Mock methods to return False
    user.is_comptable.return_value = False
    user.is_client.return_value = False
    
    # This should NOT raise AttributeError if fixed
    try:
        url = role_based_redirect(request, user)
        print(f"Success! Redirect URL: {url}")
    except AttributeError as e:
        print(f"FAIL: AttributeError raised: {e}")
    except Exception as e:
        print(f"FAIL: Unexpected error: {e}")

    # Test with administrateur
    print("\nTesting admin redirect...")
    admin_user = MagicMock()
    admin_user.is_superuser = True
    admin_user.is_administrateur = True
    
    try:
        url = role_based_redirect(request, admin_user)
        print(f"Admin Redirect URL: {url}")
        if str(url) == '/cabinet/dashboard/': # Assuming reverse_lazy resolves to this
             print("Admin redirect correct.")
    except Exception as e:
         print(f"FAIL: Admin redirect error: {e}")

if __name__ == "__main__":
    test_fix()
