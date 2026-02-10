# Guide des Rôles et Permissions

## Rôles Disponibles

### 1. **Étudiant** (ETUDIANT)
- Accès à son profil personnel
- Consultation de ses notes
- Consultation de ses cours
- Évaluation des enseignants
- Consultation des résultats
- Accès à son espace personnel

### 2. **Enseignant** (ENSEIGNANT)
- Accès à ses cours
- Saisie des appréciations
- Ajout et modification des commentaires
- Consultation du profil
- Notifications

### 3. **Jury** (JURY)
- Consultation de la grille des cours
- Gestion des évaluations
- Délibération
- Publication des résultats
- Impression des documents

### 4. **Administrateur** (ADMIN)
- **Accès complet** à tous les modules
- Gestion des utilisateurs (Étudiants, Enseignants, Jurys)
- Gestion académique (UE, EC, Cohortes, Inscriptions, Attributions)
- Configuration du système (Réglage)
- **Accès à l'historique des actions** (exclusive)
- Gestion des comptes

### 5. **Gestionnaire** (GESTIONNAIRE)
- ✅ Tous les accès de l'administrateur
- ❌ **SAUF** l'accès à l'historique des actions
- Peut configurer le système
- Peut gérer les utilisateurs et données académiques
- Utile pour les superviseurs sans besoin de suivi d'audit

### 6. **Agent** (AGENT)
- Accès **limité** à :
  - ✅ Gestion des étudiants (ajout, modification uniquement)
  - ✅ Gestion des enseignants (ajout, modification uniquement)
  - ✅ Gestion des UE/EC (ajout, modification uniquement)
  - ✅ Gestion des inscriptions (ajout, modification uniquement)
  - ❌ Pas d'accès à la gestion des jurys
  - ❌ Pas d'accès à la configuration du système
  - ❌ Pas d'accès à l'historique
  - ❌ Pas d'accès à la suppression de données

## Matrice d'Accès

| Fonction | Étudiant | Enseignant | Jury | Agent | Gestionnaire | Admin |
|----------|----------|-----------|------|-------|--------------|-------|
| Accueil Personnel | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| Gestion Étudiants | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Gestion Enseignants | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Gestion Jurys | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Gestion UE/EC | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Gestion Inscriptions | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Gestion Attributions | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Réglage Système | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Historique Actions** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Gestion Utilisateurs | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

## Utilisation des Décorateurs

### Pour les administrateurs uniquement :
```python
from core.decorators_permissions import require_admin

@require_admin
def historique_actions(request):
    # Code protégé
    pass
```

### Pour les gestionnaires et administrateurs :
```python
from core.decorators_permissions import require_gestionnaire_or_admin

@require_gestionnaire_or_admin
def gestion_jurys(request):
    # Code protégé
    pass
```

### Pour les agents, gestionnaires et administrateurs :
```python
from core.decorators_permissions import require_staff_or_roles

@require_staff_or_roles(['GESTIONNAIRE', 'AGENT'])
def gestion_etudiants(request):
    # Code protégé
    pass
```

## Création d'un Utilisateur avec un Rôle Spécifique

1. Aller à `/gestion/utilisateurs/` (administrateur)
2. Cliquer sur "Ajouter"
3. Remplir le formulaire
4. Sélectionner le rôle :
   - Étudiant
   - Enseignant
   - Jury
   - **Gestionnaire** (nouveau)
   - **Agent** (nouveau)
   - Administrateur
5. Valider

## Notes Importantes

- Les agents ne peuvent **que** ajouter et modifier, pas supprimer
- Les gestionnaires n'ont pas accès à l'historique des actions
- Les administrateurs ont **accès complet** incluant l'historique
- Les permissions sont vérifiées à la fois côté serveur (sécurité) et côté interface (UI)

## Implémentation Future

Pour une sécurité complète, les décorateurs `require_*` devraient être appliqués à **toutes** les vues correspondantes dans `core/views.py`. 

Exemple des vues à modifier avec le décorateur approprié :
- `@require_staff_or_roles(['GESTIONNAIRE', 'AGENT'])` : gestion_etudiants, gestion_enseignants, gestion_ue, gestion_ec, gestion_inscriptions
- `@require_gestionnaire_or_admin` : gestion_attributions, gestion_jurys, gestion_sections, gestion_utilisateurs
- `@require_admin` : historique_actions, statistiques
