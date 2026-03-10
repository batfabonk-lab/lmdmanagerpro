import threading
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import set_script_prefix

_thread_locals = threading.local()


def get_current_db():
    """Retourne la base de données active pour l'institution courante."""
    return getattr(_thread_locals, 'institution_db', 'default')


def get_current_institution_slug():
    """Retourne le slug de l'institution courante."""
    return getattr(_thread_locals, 'institution_slug', None)


class InstitutionMiddleware:
    """
    Middleware qui gère le routing multi-institutions par URL prefix.
    
    URL: /ista-gm/login/ → institution='ista-gm', path_info='/login/'
    URL: /ista-casa/     → institution='ista-casa', path_info='/'
    URL: /               → page de sélection d'institution
    
    Utilise set_script_prefix() pour que {% url %} génère automatiquement
    les URLs avec le bon préfixe (zéro changement dans les templates).
    """
    
    EXEMPT_PREFIXES = ('/static/', '/media/')
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        institutions = getattr(settings, 'INSTITUTIONS', {})
        
        # Si pas d'institutions configurées, laisser passer (mode normal)
        if not institutions:
            return self.get_response(request)
        
        path = request.META.get('PATH_INFO', '/')
        
        # Ne pas intercepter les fichiers statiques/media
        for prefix in self.EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return self.get_response(request)
        
        # Extraire le slug de l'URL (ne pas supprimer le slash final!)
        clean_path = path[1:] if path.startswith('/') else path
        parts = clean_path.split('/', 1)
        slug = parts[0] if parts[0] else ''
        
        if slug and slug in institutions:
            inst = institutions[slug]
            
            # Définir le contexte institution sur le thread et la request
            _thread_locals.institution_db = inst.get('database', slug)
            _thread_locals.institution_slug = slug
            request.institution_slug = slug
            request.institution_name = inst.get('name', slug)
            
            # Réécrire le PATH_INFO (enlever le préfixe institution)
            remaining = '/' + (parts[1] if len(parts) > 1 else '')
            request.META['PATH_INFO'] = remaining
            request.path_info = remaining
            
            # Recalculer request.path (SCRIPT_NAME + PATH_INFO)
            script_name = request.META.get('SCRIPT_NAME', '')
            request.path = script_name + '/' + slug + remaining
            
            # set_script_prefix pour que reverse() / {% url %} ajoute le préfixe
            set_script_prefix('/' + slug + '/')
            
            try:
                response = self.get_response(request)
            finally:
                # Nettoyer le thread-local
                _thread_locals.institution_db = 'default'
                _thread_locals.institution_slug = None
                set_script_prefix('/')
            
            return response
        
        elif path == '/' or path == '':
            # Page d'accueil : sélecteur d'institution
            return render(request, 'select_institution.html', {
                'institutions': institutions,
            })
        
        else:
            # URL inconnue → rediriger vers la page de sélection
            return HttpResponseRedirect('/')
