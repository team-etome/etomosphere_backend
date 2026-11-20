from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class UTILS:
    @staticmethod
    def is_valid_email(value: str) -> bool:
        """
        Check whether the given value is a valid email address.
        """
        if not value:
            return False

        try:
            validate_email(value.strip())
            return True
        except ValidationError:
            return False