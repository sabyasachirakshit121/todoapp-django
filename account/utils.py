
from typing import Optional, Dict, Any
from account.models import CustomUser


def get_user_info(user: CustomUser, token: Optional[str] = None) -> Dict[str, Any]:
    """Get user info."""
    user_info = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'token': token,
        'email': user.email,
        'phone_number': str(user.phone_number),
        'gender': "Male" if user.gender == 1 else "Female"
    }
    return user_info
