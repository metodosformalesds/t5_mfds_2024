from django.http import HttpResponse
from django.shortcuts import redirect

""" En proceso de analisis"""


def unauthenticated_user(view_func):
    """Decorador que maneja la logica para no dejar a un usuario autenticado 
    registrarse o logearse de nuevo

    Args:
        view_func (function): Recibe una funcion para realizar la logica del wrapper
    """
    def wrapper_func(request, *args, **kwargs):
        """ Verifica si el usuario esta autenticado y si este debe o no 
            ver el registro e inicio de sesion 
        """
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    """Decorador que permite restringir cierta vista dependiendo del tipo de usuario 

    Args:
        allowed_roles (list, optional): Una lista con los tipos de usuario de los grupos
        permitidos para ver una vista en especifico. Por default es una lista vacia [].
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None

            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('Careces de autorizacion para ver esta seccion')

        return wrapper_func
    return decorator
