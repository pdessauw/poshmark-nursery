def check_bool_input(val):
    if val in ("y", "yes", "t", "true", "1"):
        return True, True
    elif val in ("n", "no", "f", "false", "0"):
        return True, False
    else:
        return False, False
