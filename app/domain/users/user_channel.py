class UserChannel:
    def __init__(self, user):
        self.user = user

    def get_name(self):
        return f"user_channel_{self.user.id}"
