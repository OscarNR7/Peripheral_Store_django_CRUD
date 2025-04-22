from allauth.account.adapter import DefaultAccountAdapter

class NoUsernameAccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        # Evita que allauth intente asignar un username
        pass