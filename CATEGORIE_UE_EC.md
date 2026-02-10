# ✅ Colonne Catégorie Ajoutée dans UE et EC !

## 🎉 Ce qui a été Fait

J'ai ajouté une colonne `categorie` dans les modèles **UE** et **EC** qui fait référence au modèle `Categorie` de l'application réglage.

---

## 📊 Modifications des Modèles

### Modèle UE
```python
class UE(models.Model):
    code_ue = models.CharField(...)
    intitule_ue = models.CharField(...)
    credit = models.IntegerField(...)
    cmi = models.IntegerField(...)
    tp_td = models.CharField(...)
    semestre = models.IntegerField(...)
    categorie = models.ForeignKey('reglage.Categorie', 
                                   on_delete=models.SET_NULL, 
                                   null=True, 
                                   blank=True, 
                                   verbose_name='Catégorie')  # ← NOUVEAU
```

### Modèle EC
```python
class EC(models.Model):
    code_ec = models.CharField(...)
    intitule_ue = models.CharField(...)
    credit = models.IntegerField(...)
    cmi = models.IntegerField(...)
    tp_td = models.CharField(...)
    code_ue = models.ForeignKey(UE, ...)
    categorie = models.ForeignKey('reglage.Categorie', 
                                   on_delete=models.SET_NULL, 
                                   null=True, 
                                   blank=True, 
                                   verbose_name='Catégorie')  # ← NOUVEAU
```

---

## 🔗 Relation

### Type de Relation
- **ForeignKey** : Plusieurs UE/EC peuvent avoir la même catégorie
- **SET_NULL** : Si une catégorie est supprimée, le champ devient NULL
- **null=True, blank=True** : Le champ est optionnel

### Schéma
```
Categorie (reglage)
    ↑
    |
    ├── UE.categorie (FK)
    └── EC.categorie (FK)
```

---

## 📝 Formulaires Mis à Jour

### UEForm
```python
fields = ['code_ue', 'intitule_ue', 'credit', 'cmi', 'tp_td', 'semestre', 'categorie']
```

**Widget :** Dropdown (Select) avec toutes les catégories disponibles

### ECForm
```python
fields = ['code_ec', 'intitule_ue', 'credit', 'cmi', 'tp_td', 'code_ue', 'categorie']
```

**Widget :** Dropdown (Select) avec toutes les catégories disponibles

---

## 🎯 Utilisation

### Dans l'Admin Django

#### Créer/Modifier une UE
1. Allez sur `/admin/core/ue/`
2. Créez ou modifiez une UE
3. Vous verrez un nouveau champ **"Catégorie"**
4. Sélectionnez une catégorie dans le dropdown (optionnel)
5. Enregistrez

#### Créer/Modifier un EC
1. Allez sur `/admin/core/ec/`
2. Créez ou modifiez un EC
3. Vous verrez un nouveau champ **"Catégorie"**
4. Sélectionnez une catégorie dans le dropdown (optionnel)
5. Enregistrez

---

## 💡 Exemples de Catégories

### Catégories Possibles
```
CAT-FOND | Cours Fondamentaux
CAT-SPEC | Cours de Spécialisation
CAT-PROJ | Projets
CAT-STAGE | Stages
CAT-OPT | Cours Optionnels
CAT-OBLIG | Cours Obligatoires
```

### Exemple d'Utilisation
```
UE: Programmation Python
  - Code: UE-PROG-PY
  - Catégorie: CAT-FOND (Cours Fondamentaux)

EC: Introduction à Python
  - Code: EC-INTRO-PY
  - Catégorie: CAT-OBLIG (Cours Obligatoires)
```

---

## 🔍 Requêtes Possibles

### Filtrer les UE par Catégorie
```python
# Toutes les UE de la catégorie "Fondamentaux"
ues_fondamentaux = UE.objects.filter(categorie__code_categorie='CAT-FOND')

# Toutes les UE sans catégorie
ues_sans_categorie = UE.objects.filter(categorie__isnull=True)
```

### Filtrer les EC par Catégorie
```python
# Tous les EC obligatoires
ecs_obligatoires = EC.objects.filter(categorie__code_categorie='CAT-OBLIG')

# Tous les EC d'une UE avec catégorie
ecs = EC.objects.filter(code_ue__categorie__code_categorie='CAT-FOND')
```

---

## ✅ Migrations Appliquées

```bash
✅ core.0003_ec_categorie_ue_categorie
```

**Changements :**
- Ajout de la colonne `categorie_id` dans la table `core_ue`
- Ajout de la colonne `categorie_id` dans la table `core_ec`
- Clé étrangère vers `reglage_categorie`

---

## 📁 Fichiers Modifiés

### Modèles
- ✅ `core/models.py` - Ajout du champ `categorie` dans UE et EC

### Formulaires
- ✅ `core/forms.py` - Ajout du champ `categorie` dans UEForm et ECForm

### Migrations
- ✅ `core/migrations/0003_ec_categorie_ue_categorie.py`

---

## 🎨 Interface Admin

### Champ Catégorie
- **Type :** Dropdown (Select)
- **Options :** Toutes les catégories de `reglage.Categorie`
- **Optionnel :** Oui (peut être vide)
- **Affichage :** Code + Désignation

### Exemple de Dropdown
```
[Sélectionnez une catégorie]
CAT-FOND - Cours Fondamentaux
CAT-SPEC - Cours de Spécialisation
CAT-PROJ - Projets
CAT-STAGE - Stages
CAT-OPT - Cours Optionnels
CAT-OBLIG - Cours Obligatoires
```

---

## 🔄 Workflow

### 1. Créer des Catégories
```
/admin/reglage/categorie/
```
Créez d'abord les catégories que vous voulez utiliser.

### 2. Assigner aux UE
```
/admin/core/ue/
```
Lors de la création/modification d'une UE, sélectionnez une catégorie.

### 3. Assigner aux EC
```
/admin/core/ec/
```
Lors de la création/modification d'un EC, sélectionnez une catégorie.

---

## 📊 Avantages

### Organisation
- ✅ Classifier les UE/EC par type
- ✅ Regrouper les cours similaires
- ✅ Faciliter la recherche et le filtrage

### Reporting
- ✅ Statistiques par catégorie
- ✅ Nombre d'UE/EC par catégorie
- ✅ Crédits totaux par catégorie

### Gestion
- ✅ Planification des cours
- ✅ Attribution des enseignants
- ✅ Organisation des emplois du temps

---

## 🚀 Prochaines Étapes

### Affichage dans les Templates
Mettre à jour les templates de gestion pour afficher la catégorie :
```html
<td>
    {% if ue.categorie %}
        <span class="badge bg-secondary">{{ ue.categorie.designation_categorie }}</span>
    {% else %}
        <span class="text-muted">Non catégorisé</span>
    {% endif %}
</td>
```

### Filtres dans les Vues
Ajouter des filtres par catégorie dans les pages de gestion.

### Statistiques
Créer des rapports par catégorie.

---

## 🎉 Résultat

**Les modèles UE et EC ont maintenant un champ catégorie :**
- ✅ Relation avec le modèle Categorie
- ✅ Champ optionnel
- ✅ Dropdown dans les formulaires
- ✅ Migrations appliquées

**Testez dans l'admin Django !** 🚀

**http://localhost:8000/admin/core/ue/** 📚
**http://localhost:8000/admin/core/ec/** 📝
