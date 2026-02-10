# 📚 Scénarios "Passage Automatique" - Nouvelle Architecture

## 🔧 Modifications de base

### 1. Ajouter `annee_academique` à Evaluation

```python
# core/models.py - Classe Evaluation

class Evaluation(models.Model):
    id_ev = models.AutoField(primary_key=True, verbose_name='ID Évaluation')
    cc = models.FloatField(validators=[...], verbose_name='Note CC', null=True, blank=True)
    examen = models.FloatField(validators=[...], verbose_name='Note Examen', null=True, blank=True)
    rattrapage = models.FloatField(validators=[...], null=True, blank=True)
    rachat = models.FloatField(validators=[...], null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_COURS')
    code_ue = models.ForeignKey(UE, on_delete=models.CASCADE, null=True, blank=True)
    matricule_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    code_ec = models.ForeignKey(EC, on_delete=models.CASCADE, null=True, blank=True)
    annee_academique = models.CharField(max_length=10, verbose_name='Année Académique', default='2025-2026')
    
    class Meta:
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'
        # ✨ MODIFIÉ: Ajout annee_academique
        unique_together = ['matricule_etudiant', 'code_ue', 'code_ec', 'annee_academique']
```

### 2. Créer la table InscriptionUE (pour les dettes compensées)

```python
# core/models.py - Nouveau modèle

class InscriptionUE(models.Model):
    TYPE_CHOICES = [
        ('DETTE_COMPENSEE', 'Dette compensée (à reprendre)'),
        ('DETTE_REDOUBLEMENT', 'Dette doublant (à reprendre)'),  # Optionnel si besoin
    ]
    
    code_inscription_ue = models.AutoField(primary_key=True)
    matricule_etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    code_ue = models.ForeignKey(UE, on_delete=models.CASCADE, null=True, blank=True)
    code_ec = models.ForeignKey(EC, on_delete=models.CASCADE, null=True, blank=True)
    annee_academique = models.CharField(max_length=10, verbose_name='Année Académique')
    code_classe = models.ForeignKey('reglage.Classe', on_delete=models.CASCADE, verbose_name='Classe d\'origine (pour dettes)')
    type_inscription = models.CharField(max_length=30, choices=TYPE_CHOICES, default='DETTE_COMPENSEE')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Inscription UE'
        verbose_name_plural = 'Inscriptions UE'
        unique_together = ['matricule_etudiant', 'code_ue', 'code_ec', 'annee_academique', 'code_classe']
    
    def __str__(self):
        ue_code = self.code_ue.code_ue if self.code_ue else self.code_ec.code_ec
        return f"{self.matricule_etudiant} - {ue_code} - {self.annee_academique} (Dette)"
```

---

## 📊 Scénario 1: ADMIS ✅

**Décision: Admis avec crédits > seuil**

### Flux:

```
Étudiant: Ali
Classe actuelle: L2-INFO
Année actuelle: 2025-2026
Crédits validés: 55/60
Moyenne annuelle: 12/20

↓ PASSAGE AUTOMATIQUE DÉCLENCHÉ

1. Déterminer classe suivante
   L2 → L3 (classe_suivante = L3-INFO)

2. Vérification crédits:
   ✅ Admis simple: 55 crédits validés sur 60
   ✅ Créer inscription L3 pour 2026-2027

3. Créer Inscription normalement
   Inscription(
       code_inscription='INS-ALI-2026-2027',
       matricule_etudiant=Ali,
       code_classe=L3-INFO,
       annee_academique='2026-2027',
       cohorte=cohorte_L2  ← Même cohorte
   )

4. Aucune action supplémentaire (pas de dettes, pas doublant)

5. Résultat:
   ✅ Ali inscrit en L3-INFO 2026-2027
   ✅ Prêt pour évaluation L3 normale
   ✅ Historique: Evaluation(ALI, UE, 2025-2026) conservé
```

### Base de données après:

```sql
-- Inscription
| code_classe | matricule | annee_academique |
|-------------|-----------|------------------|
| L3-INFO     | ALI       | 2026-2027        | ← NEW

-- Evaluation (2025-2026) conservée
| matricule | code_ue | annee_academique | cc | examen | rachat |
|-----------|---------|------------------|----|----|--------|
| ALI       | ALGO    | 2025-2026        | 8  | 6  | NULL   |
| ALI       | ANALYSE | 2025-2026        | 7  | 5  | NULL   |

-- Evaluation (2026-2027) vide, à remplir
| matricule | code_ue | annee_academique | cc | examen |
|-----------|---------|------------------|----|----|
| ALI       | ALGÈBRE | 2026-2027        | NULL | NULL | ← Enseignant L3 remplira

```

---

## 🆙 Scénario 2: COMPENSÉ (Admis avec dette) 🔄

**Décision: Admis avec dette (compensation annuelle)**

### Flux:

```
Étudiant: Bob
Classe actuelle: L2-INFO
Année actuelle: 2025-2026
Cours L2:
  - Algèbre: 7/20 (NON_VALIDE - NOTE < 10)
  - Analyse: 13/20 (VALIDE)
Moyenne semestre: 10.5/20
→ Compensation annuelle appliquée → Algèbre passe VALIDE_COMP

Crédits validés: 45/60 (75%)
Moyenne annuelle: 10/20 ✓

↓ PASSAGE AUTOMATIQUE DÉCLENCHÉ

1. Décision = "Admis avec dette" (ADMD)
   Moyenne >= 10 ET crédits validés 60-100%

2. ✨ DOUBLE INSCRIPTION:
   
   a) Inscription PRINCIPALE (L3):
      Inscription(
          matricule_etudiant=Bob,
          code_classe=L3-INFO,          ← NOUVELLE CLASSE
          annee_academique='2026-2027'
      )
   
   b) Inscription TEMPORAIRE (L2):
      ❌ NE PAS créer d'inscription L2 2026-2027
      (Bob reste inscrit L2 2025-2026 uniquement)

3. ✨ IDENTIFIER LES DETTES (NON_VALIDE l'année N):
   Deliberation.objects.filter(
       matricule_etudiant=Bob,
       score_classe=L2,
       annee_academique='2025-2026',
       statut='NON_VALIDE'  ← Avant compensation
   )
   
   Résultat: Algèbre (7/20) NON compensée? 
   Ou le 7/20 → 10/20 par compensation?
   
   **DÉCISION: Si compensation appliquée**
   → Pas de dettes, juste passage normal
   
   **DÉCISION: Si avant compensation**
   → Bob a 1 dette: Algèbre

4. ✨ CRÉER INSCRIPTIONUE POUR LES DETTES:
   
   InscriptionUE(
       matricule_etudiant=Bob,
       code_ue=Algèbre,
       annee_academique='2026-2027',  ← Année suivante
       code_classe=L2-INFO,            ← Classe d'origine de la dette
       type_inscription='DETTE_COMPENSEE'
   )

5. L'enseignant L2 verra:
   - Inscription L2 2025-2026 → Bob (historique)
   - PLUS: InscriptionUE pour Algèbre 2026-2027 (à ré-évaluer)

6. Résultat:
   ✅ Bob inscrit en L3 2026-2027
   ✅ Bob aussi marqué pour "révaluer Algèbre L2"
   ✅ Enseignant L2 peut entrer les nouvelles notes
```

### Base de données après:

```sql
-- Inscription DOUBLE: Bob est en L2 (historique) et L3 (nouveau)
| code_classe | matricule | annee_academique |
|-------------|-----------|------------------|
| L2-INFO     | BOB       | 2025-2026        | ← Historique
| L3-INFO     | BOB       | 2026-2027        | ← NEW (passage compensé)

-- InscriptionUE: Dette à reprendre
| matricule | code_ue | annee_academique | code_classe | type_inscription |
|-----------|---------|------------------|-------------|------------------|
| BOB       | ALGO    | 2026-2027        | L2-INFO     | DETTE_COMPENSEE  | ← NEW

-- Deliberation L2 (avant compensation)
| matricule | code_ue | annee_academique | cc | examen | statut |
|-----------|---------|------------------|----|----|--------|
| BOB       | ALGO    | 2025-2026        | 4  | 3  | NON_VALIDE |
| BOB       | ANALYSE | 2025-2026        | 7  | 6  | VALIDE |

-- Evaluation L2 (enseignant peut modifier):
| matricule | code_ue | annee_academique | cc | examen |
|-----------|---------|------------------|----|----|
| BOB       | ALGO    | 2025-2026        | 4  | 3  | ← Historique conservé

-- Evaluation pour la dette (à remplir année N+1):
| matricule | code_ue | annee_academique | cc | examen |
|-----------|---------|------------------|----|----|
| BOB       | ALGO    | 2026-2027        | NULL | NULL | ← Enseignant L2 remplira en 2026-2027
```

### 🎯 Flux enseignant L2 en 2026-2027:

```
Enseignant L2 ouvre "Évaluer Algèbre L2":

SELECT Inscription 
WHERE code_classe = L2
  AND annee_academique = 2026-2027

Résultat: ❌ Bob n'est pas inscrit en L2 2026-2027!

MAIS ensuite:

SELECT InscriptionUE 
WHERE code_ue = ALGO
  AND code_classe = L2
  AND annee_academique = 2026-2027
  AND type_inscription = 'DETTE_COMPENSEE'

Résultat: ✅ Bob est marqué pour dette Algèbre!

Enseignant voit Bob dans la grille (via InscriptionUE)
Lui attribue une nouvelle note CC et Examen
→ Evaluation(Bob, ALGO, 2026-2027) remplie

Ensuite: 
- Jury L2 peut délibérer sur cette évaluation
- Deliberation créée pour la dette
- Si validée: effacer InscriptionUE, garder Deliberation VALIDE
```

---

## 🔁 Scénario 3: AJOURNÉ / DÉFAILLANT ⚠️

**Décision: Ajourné ou Défaillant (redoublement)**

### Flux:

```
Étudiant: Charlie
Classe actuelle: L2-INFO
Année actuelle: 2025-2026
Résultats:
  - Algèbre: 5/20 ❌
  - Analyse: 8/20 ❌
  - Programmation: 9/20 ❌
Crédits validés: 10/60 (17%)
Moyenne annuelle: 7.3/20 ✗

Décision: AJOURNÉ (< 60% de crédits validés)

↓ PASSAGE AUTOMATIQUE DÉCLENCHÉ

1. Identifier classe suivante → L3
   MAIS: Doublant → Reste en même classe!
   classe_redoublement = L2-INFO

2. Créer inscription redoublement:
   Inscription(
       code_inscription='INS-CHARLIE-2026-2027-REDBL',
       matricule_etudiant=Charlie,
       code_classe=L2-INFO,           ← MÊME CLASSE (redoublement)
       annee_academique='2026-2027',
       cohorte=nouvelle_cohorte        ← Cohorte auto-créée
   )

3. ✨ TRANSFERT INTELLIGIBLE DES ÉVALUATIONS:
   
   a) Récupérer Deliberation L2 2025-2026:
      - Algèbre: 5/20 (NON → transfert?)
      - Analyse: 8/20 (NON → transfert?)
      - Programmation: 9/20 (NON → transfert?)
   
   b) ✨ Copier SEULEMENT notes >= 10 dans Evaluation 2026-2027:
      
      for delib in deliberations:
          if delib.note_finale >= 10:
              Evaluation.objects.create(
                  matricule_etudiant=Charlie,
                  code_ue=delib.code_ue,
                  code_ec=delib.code_ec,
                  annee_academique='2026-2027',
                  cc=delib.cc,
                  examen=delib.examen,
                  rattrapage=delib.rattrapage,
                  rachat=delib.rachat
              )
      
      Résultat: Aucune Evaluation créée (aucune >= 10)

4. Crédits < 10: À REPRENDRE À ZÉRO
   - Algèbre, Analyse, Programmation
   - Enseignant L2 verra Charlie à nouveau
   - Notes seront vierges (NULL)
   - Charlie réévalue normalement

5. Résultat:
   ✅ Charlie réinscrit L2-INFO 2026-2027
   ✅ Pas d'historique de notes (à refaire)
   ✅ Enseignant le voit normalement dans la classe
```

### Base de données après:

```sql
-- Inscription REDOUBLEMENT
| code_classe | matricule | annee_academique |
|-------------|-----------|------------------|
| L2-INFO     | CHARLIE   | 2025-2026        | ← Historique
| L2-INFO     | CHARLIE   | 2026-2027        | ← NEW (redoublement)

-- Evaluation L2 2025-2026 (historique conservé)
| matricule | code_ue | annee_academique | cc | examen | note_finale |
|-----------|---------|------------------|----|----|-----|
| CHARLIE   | ALGO    | 2025-2026        | 2  | 3  | 5   | ← Historique

-- Evaluation L2 2026-2027 (vierge, à remplir)
| matricule | code_ue | annee_academique | cc | examen |
|-----------|---------|------------------|----|----|
| CHARLIE   | ALGO    | 2026-2027        | NULL | NULL | ← À refaire
| CHARLIE   | ANALYSE | 2026-2027        | NULL | NULL | ← À refaire
| CHARLIE   | PROG    | 2026-2027        | NULL | NULL | ← À refaire

-- Aucune InscriptionUE créée pour Charlie (doublant)
```

### 🎯 Variante: Doublant avec quelques notes >= 10

```
Étudiant: Diana
Résultats:
  - Algèbre: 5/20 ❌
  - Analyse: 11/20 ✅
  - Programmation: 12/20 ✅

Redoublement créé:
- Inscription L2 2026-2027

Transfert des notes >= 10:
  Evaluation(Diana, ANALYSE, 2026-2027) = cc=6, examen=5
  Evaluation(Diana, PROG, 2026-2027) = cc=7, examen=5

Résultat:
- Diana rédouble L2
- Analyse et Programmation: pré-remplies (elle peut les refaire)
- Algèbre: à zéro uniquement
```

---

## 📋 Résumé comparatif

| Critère | ADMIS | COMPENSÉ | AJOURNÉ/DÉFAILLANT |
|---------|-------|----------|------------------|
| **Classe suivante** | L2 → L3 | L2 → L3 | L2 → L2 (redbl) |
| **Inscription classe** | INS L3 N+1 | INS L3 N+1 | INS L2 N+1 |
| **InscriptionUE** | ❌ Non | ✅ OUI (dettes) | ❌ Non |
| **Éval transférées** | ❌ Aucune | ❌ Aucune | ✅ >= 10 seulement |
| **Cohorte** | Ancienne | Ancienne | Nouvelle (auto-créée) |
| **Enseignant voit** | Nouveau cours | Cours L2 + dettes L2 | Anciens cours |
| **Double inscr.** | Non | Non (mais L2 L2 historique + L3 nouveau) | Non |

---

## 🔧 Modifications de code nécessaires

### 1. Modifier `Evaluation` model
- ✅ Ajouter `annee_academique` (CharField, max_length=10)
- ✅ Modifier `unique_together`
- ✅ Créer migration Django

### 2. Créer `InscriptionUE` model ✨
- Créer la classe
- Migrer

### 3. Modifier `enseignant_evaluer_cours` view
```python
# Récupérer les étudiants (ACTUEL)
inscriptions = Inscription.objects.filter(
    code_classe=L2,
    annee_academique='2026-2027'
)

# NOUVEAU: Ajouter aussi les dettes
inscriptions_ue = InscriptionUE.objects.filter(
    code_ue=cours_ue,
    annee_academique='2026-2027',
    type_inscription='DETTE_COMPENSEE'
)

# Fusionner les 2 listes pour affichage
```

### 4. Modifier `_jury_compute_delib_ues` view
- Ajouter filtre `annee_academique` partout
- Optionnel: retriever dettes pour info profil

### 5. Créer `recuperer_dettes_classe_inferieure` function
```python
def recuperer_dettes_classe_inferieure(etudiant, classe_obj, annee_academique):
    """Récupère les dettes (NON_VALIDE) de la classe inférieure pour affichage profil"""
    # Maper classe (L3 → L2, M1 → L3, etc)
    # Retourner Deliberation statut NON_VALIDE
```

### 6. Modifier templates profil/relevé
- Ajouter section "Dettes à reprendre"
- Affichage informatif uniquement

---

## 🚀 Implémentation

### Phase 1: Modèles
1. Ajouter `annee_academique` à Evaluation
2. Créer InscriptionUE
3. Migrer

### Phase 2: Views (passage automatique)
Modifier `views_passage_automatique.py`:
- Scénario 1 (Admis): Pas de code changement majeur
- Scénario 2 (Compensé): Créer InscriptionUE au lieu de Deliberation
- Scénario 3 (Ajourné): Créer Evaluation (au lieu de Deliberation)

### Phase 3: Enseignants
Modifier `enseignant_evaluer_cours`:
- Afficher aussi InscriptionUE dettes
- Laisser modifier les notes

### Phase 4: Affichage
Modifier profils/relevés:
- Afficher dettes (informatif)
- Utiliser `recuperer_dettes_classe_inferieure()`

