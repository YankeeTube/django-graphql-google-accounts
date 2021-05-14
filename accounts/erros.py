class TokenRequestFailed(Exception):

    def __str__(self):
        return 'Google get token load failed ...'


class NotFoundIDToken(Exception):

    def __str__(self):
        return 'Not Found Google ID Token ...'
