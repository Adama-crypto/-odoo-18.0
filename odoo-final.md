# Objectif du travail

Vous devez compléter le module Estate en ajoutant des menus, des vues et des relations entre les modèles.

Le module doit permettre de gérer :

- Les locataires
- Les locations
- Les interventions
- Les pièces
- Les types de pièces

---

## Menus à ajouter

| Menu | Description |
| --- | --- |
| Locations | Gérer les locations de propriétés |
| Locataires | Utilise le modèle Contact d'Odoo |
| Interventions | Gérer les interventions liées aux propriétés |
| Pièces | Gérer les pièces d'une propriété |
| Types de pièces | Définir les catégories de pièces |

---

## 1. Menu Locations

Le menu Locations doit permettre de gérer les locations des propriétés.

### Vues requises

- Vue formulaire
- Vue liste
- Vue kanban
- Vue calendrier
- Vue graphique
- Vue de recherche personnalisée

### Champs du formulaire

| Champ | Remarque |
| --- | --- |
| Locataire | |
| Propriété | |
| Date de réservation | |
| Date de début | |
| Date de fin | |
| Durée | Ce champ doit être calculé automatiquement à partir des dates de début et de fin. Ne pas le saisir manuellement. |
| Fréquence de paiement | |
| Loyer | |
| États des lieux | |

### Statuts de la location

| Statut |
| --- |
| Brouillon |
| Validée |
| En cours |
| Annulée |

---

## 2. Menu Locataires

Le menu Locataires doit utiliser le modèle Contact d'Odoo. Ne créez pas un nouveau modèle.

- Hériter de la vue formulaire du module Contact
- Ajouter un onglet « Locations » dans la fiche du contact (Cet onglet affiche toutes les locations effectuées par ce locataire)

---

## 3. Menu Interventions

Le menu Interventions doit permettre de gérer les interventions liées aux propriétés.

### Champs de la fiche

| Champ |
| --- |
| Référence |
| Date |
| Type |
| Propriété |
| Description |
| Statut |

### Statuts

| Statut |
| --- |
| Planifiée |
| En cours |
| Terminée |

---

## 4. Menu Pièces

Le menu Pièces doit permettre de gérer les pièces d'une propriété.

### Champs de la fiche

| Champ |
| --- |
| Nom |
| Type de pièce |
| Propriété |
| Superficie |

---

## 5. Menu Types de pièces

Le menu Types de pièces doit permettre de définir les catégories de pièces.

### Champs

| Champ |
| --- |
| Libellé |
| Description |
| Liste des pièces liées à ce type |

---

## Modification du menu Propriétés

Les champs existants de la vue formulaire Propriété ne doivent pas être modifiés.

### Statuts à ajouter

| Statut |
| --- |
| Libre |
| Occupée |
| Réservée |

### Onglet Pièces à ajouter

Ajouter un onglet **Pièces** dans la fiche propriété. Chaque ligne doit afficher :

| Colonne |
| --- |
| Nom de la pièce |
| Type de pièce |
| Superficie |

---

> **NB :** Vous devez intégrer des restrictions de logique métier dans votre module.
