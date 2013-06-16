from django.core.exceptions import ValidationError

class BadFormat(Exception):
    """
    An exception specifying that the supplied tweet
    was not of a suitable format to be treated as a #upkarma tweet
    """
    pass

class Banned(ValidationError):
    """
    An exception specifying
    that a user has been banned from the game
    """
    pass

class SenderBanned(ValidationError):
    """
    A specific Banned exception
    used when the banned user
    is the sender
    """
    pass

class ReceiverBanned(ValidationError):
    """
    A specific Banned exception
    used when the banned user
    is the receiver
    """
    pass
