import re


class Util:
    """
    工具类
    """
    @staticmethod
    def is_valid_int(s):
        return bool(re.match(r'^[+-]?\d+$', s))

    @staticmethod
    def safe_str_to_int(s):
        if Util.is_valid_int(s):
            return int(s)
        else:
            print(f"无效的整数格式: '{s}'")
            return None

    @staticmethod
    def str_to_bool(s):
        if isinstance(s, str):
            s = s.strip().lower()
            if s in ('true', 'yes', '1'):
                return True
            elif s in ('false', 'no', '0'):
                return False
        raise ValueError(f"Cannot convert {s} to bool")
