from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackend(ModelBackend):
    """
    Author: Santiago Mendivil 
    Custom authentication backend that allows users to log in using their email address.

    Methods
    -------
    authenticate(request, email=None, password=None, **kwargs)
        Authenticates a user based on the provided email and password.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    email : str, optional
        The email address of the user attempting to authenticate.
    password : str, optional
        The password of the user attempting to authenticate.
    **kwargs : dict
        Additional keyword arguments.

    Returns
    -------
    user : UserModel instance or None
        Returns the authenticated user if the email and password are correct.
        Returns None if the user does not exist or the password is incorrect.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
