"""
Décorateurs et helpers pour les contrôles de permissions basés sur les rôles
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def require_admin(view_func):
    """Décorateur : Réserve l'accès aux administrateurs"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_staff and request.user.role == 'ADMIN'):
            messages.error(request, 'Accès réservé aux administrateurs.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_gestionnaire_or_admin(view_func):
    """Décorateur : Réserve l'accès aux gestionnaires et administrateurs"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.role in ['ADMIN', 'GESTIONNAIRE']):
            messages.error(request, 'Accès réservé aux gestionnaires et administrateurs.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_staff_or_roles(roles):
    """Décorateur générique : Accepte les admins et les rôles spécifiés"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            allowed_roles = ['ADMIN'] + roles if 'ADMIN' not in roles else roles
            if not (request.user.is_staff or request.user.role in allowed_roles):
                messages.error(request, 'Accès non autorisé.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# EXEMPLE D'UTILISATION DANS LES VUES
# ===================================
# 
# Administrateur uniquement :
# @require_admin
# def historique_actions(request):
#     ...
# 
# Gestionnaire + Administrateur :
# @require_gestionnaire_or_admin
# def gestion_jurys(request):
#     ...
# 
# Gestionnaire + Agent + Administrateur :
# @require_staff_or_roles(['GESTIONNAIRE', 'AGENT'])
# def gestion_etudiants(request):
#     ...
