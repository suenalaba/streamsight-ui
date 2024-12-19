def split_string_by_last_underscore(s: str):
    before, after = s.rsplit("_", 1)
    return before, after
