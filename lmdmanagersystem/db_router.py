from lmdmanagersystem.middleware import get_current_db


class InstitutionRouter:
    """
    Database router qui dirige les requêtes vers la BD de l'institution active.
    
    Chaque institution a sa propre base de données MySQL.
    Le middleware définit quelle BD utiliser via un thread-local.
    """
    
    def db_for_read(self, model, **hints):
        return get_current_db()
    
    def db_for_write(self, model, **hints):
        return get_current_db()
    
    def allow_relation(self, obj1, obj2, **hints):
        # Autoriser les relations entre objets de la même BD
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Autoriser les migrations sur toutes les BD
        return True
