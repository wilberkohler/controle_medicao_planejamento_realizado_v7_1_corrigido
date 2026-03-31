class AppContext:
    def __init__(self):
        self.current_user = None

    def set_current_user(self, user_row):
        self.current_user = user_row

    def current_user_id(self):
        if not self.current_user:
            return None
        try:
            return self.current_user["id"]
        except Exception:
            return None

    def current_user_name(self):
        if not self.current_user:
            return ""
        try:
            return self.current_user["nome"] or ""
        except Exception:
            return ""
