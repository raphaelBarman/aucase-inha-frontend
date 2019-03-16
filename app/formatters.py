
from sqlalchemy import types

class StrippedString(types.TypeDecorator):
    """
    Returns CHAR values with spaces stripped
    """

    impl = types.String

    def process_bind_param(self, value, dialect):
        "No-op"
        return value

    def process_result_value(self, value, dialect):
        """
        Strip the trailing spaces on resulting values.
        If value is false, we return it as-is; it might be none
        for nullable columns
        """
        return value.strip() if value else value

    def copy(self):
        "Make a copy of this type"
        return StrippedString(self.impl.length)
