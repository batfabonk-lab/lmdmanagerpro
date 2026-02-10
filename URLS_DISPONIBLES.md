# 🌐 URLs Disponibles - Système LMD

## Liste Complète des URLs

### 🏠 Pages Publiques

| URL | Nom | Description | Accès |
|-----|-----|-------------|-------|
| `/` | home | Page d'accueil | Public |
| `/login/` | login | Page de connexion | Public |
| `/logout/` | logout | Déconnexion | Authentifié |

---

### 👨‍🎓 Espace Étudiant

| URL | Nom | Description | Accès |
|-----|-----|-------------|-------|
| `/etudiant/` | etudiant_dashboard | Tableau de bord étudiant | Étudiant |
| `/etudiant/notes/` | etudiant_notes | Consultation des notes | Étudiant |

**Fonctionnalités :**
- ✅ Voir ses informations personnelles
- ✅ Consulter ses inscriptions
- ✅ Voir sa moyenne générale
- ✅ Consulter ses notes par UE et EC
- ✅ Voir le statut de validation

---

### 👨‍🏫 Espace Enseignant

| URL | Nom | Description | Accès |
|-----|-----|-------------|-------|
| `/enseignant/` | enseignant_dashboard | Tableau de bord enseignant | Enseignant |
| `/enseignant/encoder/` | enseignant_encoder_notes | Encodage des notes | Enseignant |

**Fonctionnalités :**
- ✅ Voir les statistiques d'évaluations
- ✅ Encoder les notes (CC, Examen)
- ✅ Ajouter Rattrapage et Rachat
- ✅ Modification via interface modale
- ✅ Validation automatique des statuts

---

### 👥 Espace Jury

| URL | Nom | Description | Accès |
|-----|-----|-------------|-------|
| `/jury/` | jury_dashboard | Tableau de bord jury | Jury |
| `/jury/deliberer/` | jury_deliberer | Délibération | Jury |
| `/jury/publier/` | jury_publier | Publication des résultats | Jury |

**Fonctionnalités :**
- ✅ Voir la composition du jury
- ✅ Liste des étudiants de la classe
- ✅ Délibération avec moyennes automatiques
- ✅ Décisions automatiques (Admis/Ajourné)
- ✅ Publication officielle des résultats

---

### 🔧 Administration Django

| URL | Description | Accès |
|-----|-------------|-------|
| `/admin/` | Interface d'administration Django | Admin |
| `/admin/core/user/` | Gestion des utilisateurs | Admin |
| `/admin/core/etudiant/` | Gestion des étudiants | Admin |
| `/admin/core/enseignant/` | Gestion des enseignants | Admin |
| `/admin/core/jury/` | Gestion des jurys | Admin |
| `/admin/core/ue/` | Gestion des UE | Admin |
| `/admin/core/ec/` | Gestion des EC | Admin |
| `/admin/core/evaluation/` | Gestion des évaluations | Admin |
| `/admin/core/inscription/` | Gestion des inscriptions | Admin |
| `/admin/core/cohorte/` | Gestion des cohortes | Admin |
| `/admin/core/classe/` | Gestion des classes | Admin |
| `/admin/core/section/` | Gestion des sections | Admin |
| `/admin/core/departement/` | Gestion des départements | Admin |

---

## 🔄 Redirections Automatiques

### Après Connexion
```
Rôle ETUDIANT    → /etudiant/
Rôle ENSEIGNANT  → /enseignant/
Rôle JURY        → /jury/
Rôle ADMIN       → / (ou /admin/)
```

### Si Non Authentifié
```
Toute URL protégée → /login/
```

### Après Déconnexion
```
/logout/ → /login/
```

---

## 📊 Exemples d'Utilisation

### 1. Étudiant Consulte ses Notes

```
1. Naviguer vers http://localhost:8000/
2. Cliquer sur "Se connecter"
3. Entrer: etudiant1 / etudiant123
4. Redirection automatique vers /etudiant/
5. Cliquer sur "Mes Notes"
6. URL finale: http://localhost:8000/etudiant/notes/
```

### 2. Enseignant Encode des Notes

```
1. Naviguer vers http://localhost:8000/login/
2. Entrer: enseignant1 / enseignant123
3. Redirection automatique vers /enseignant/
4. Cliquer sur "Encoder Notes"
5. URL finale: http://localhost:8000/enseignant/encoder/
6. Modifier une note et enregistrer
```

### 3. Jury Délibère

```
1. Naviguer vers http://localhost:8000/login/
2. Entrer: jury1 / jury123
3. Redirection automatique vers /jury/
4. Cliquer sur "Délibérer"
5. URL finale: http://localhost:8000/jury/deliberer/
6. Voir les moyennes et décisions
```

### 4. Admin Gère les Données

```
1. Naviguer vers http://localhost:8000/admin/
2. Entrer: admin / admin123
3. Sélectionner un modèle (ex: Étudiants)
4. URL: http://localhost:8000/admin/core/etudiant/
5. Ajouter/Modifier/Supprimer des données
```

---

## 🔐 Contrôle d'Accès

### URLs Publiques (Aucune authentification requise)
- `/` - Page d'accueil
- `/login/` - Connexion

### URLs Protégées (Authentification requise)
- `/etudiant/*` - Réservé aux étudiants
- `/enseignant/*` - Réservé aux enseignants
- `/jury/*` - Réservé aux jurys
- `/admin/*` - Réservé aux administrateurs

### Vérification dans les Vues
```python
@login_required
def etudiant_dashboard(request):
    try:
        etudiant = Etudiant.objects.get(id_lgn=request.user)
        # ...
    except Etudiant.DoesNotExist:
        messages.error(request, 'Profil étudiant non trouvé.')
        return redirect('home')
```

---

## 📱 URLs pour API (Future Extension)

### Suggestions pour API REST
```
/api/etudiants/                    # Liste des étudiants
/api/etudiants/<matricule>/        # Détail étudiant
/api/evaluations/                  # Liste des évaluations
/api/evaluations/<id>/             # Détail évaluation
/api/notes/<matricule>/            # Notes d'un étudiant
/api/deliberation/<classe>/        # Résultats délibération
```

---

## 🎯 Navigation Recommandée

### Pour Tester le Système

1. **Commencer par l'Admin**
   ```
   http://localhost:8000/admin/
   → Voir toutes les données
   → Comprendre la structure
   ```

2. **Tester l'Étudiant**
   ```
   http://localhost:8000/login/
   → etudiant1 / etudiant123
   → Voir le dashboard
   → Consulter les notes
   ```

3. **Tester l'Enseignant**
   ```
   http://localhost:8000/login/
   → enseignant1 / enseignant123
   → Encoder des notes
   → Voir la validation automatique
   ```

4. **Tester le Jury**
   ```
   http://localhost:8000/login/
   → jury1 / jury123
   → Délibérer
   → Publier les résultats
   ```

---

## 🔍 Débogage

### Vérifier les URLs Disponibles
```bash
python manage.py show_urls
```

### Tester une URL
```bash
curl http://localhost:8000/
curl http://localhost:8000/etudiant/
```

### Logs du Serveur
Le serveur affiche toutes les requêtes :
```
[08/Dec/2024 13:00:00] "GET / HTTP/1.1" 200 1234
[08/Dec/2024 13:00:05] "GET /login/ HTTP/1.1" 200 5678
[08/Dec/2024 13:00:10] "POST /login/ HTTP/1.1" 302 0
```

---

## 📝 Notes Importantes

### URLs Sensibles à la Casse
- Django est sensible à la casse pour les URLs
- `/Etudiant/` ≠ `/etudiant/`
- Toujours utiliser les minuscules

### Trailing Slash
- Django ajoute automatiquement le `/` final
- `/etudiant` → redirige vers `/etudiant/`
- Recommandé : toujours inclure le `/` final

### Paramètres GET
Exemples pour futures extensions :
```
/etudiant/notes/?semestre=1
/enseignant/encoder/?classe=L1-INFO-A
/jury/deliberer/?annee=2024-2025
```

---

## 🎓 Résumé

**Total URLs Implémentées : 13**
- 3 URLs publiques
- 2 URLs étudiant
- 2 URLs enseignant
- 3 URLs jury
- 1 URL admin (+ sous-URLs)
- 2 URLs authentification

**Toutes les URLs sont fonctionnelles et testées !** ✅

---

**Pour accéder à l'application : http://localhost:8000/** 🚀
