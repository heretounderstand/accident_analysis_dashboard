# Analyse des accidents de la route

Tableau de bord Streamlit d'analyse de 132 000 accidents de la route (10 pays, 2000 – 2024) :
géographie, évolution temporelle, environnement, conducteurs, véhicules et impact financier,
avec un audit de la qualité des données.

## Lancer l'application

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

Tests :

```bash
pip install -r requirements-dev.txt
```

```bash
python -m pytest
```

## Démarche analytique

- **Indicateurs par accident** (décès, blessés, part d'accidents mortels, coût moyen) plutôt
  que des totaux, qui dépendent surtout de la taille des groupes.
- **Intervalles de confiance à 95 %** sur toutes les moyennes comparées.
- **Tests statistiques** : Kruskal-Wallis (indicateurs numériques) et Khi² (proportions),
  correction de Bonferroni pour les tests multiples, et **tailles d'effet** (ε², V de Cramér)
  pour distinguer « significatif » et « important ».
- **Décomposition STL** pour séparer tendance et saisonnalité.
- **Audit des données** : complétude, doublons, plages de valeurs, cohérence logique,
  uniformité des distributions et corrélations.

### Limites du jeu de données

L'audit montre que le fichier est très probablement **synthétique** : distributions
quasi uniformes, corrélations nulles entre toutes les variables, champ `Region` incohérent avec
`Country` (corrigé : le continent est recalculé à partir du pays), gravité déclarée sans lien
avec le nombre de décès ni avec le coût. Les résultats illustrent une méthode d'analyse et ne
doivent pas être lus comme des constats réels sur la sécurité routière.

## Structure

```
app.py                  Point d'entrée : navigation, filtres globaux
.streamlit/config.toml  Thème
src/
  config.py             Libellés, traductions, ordres des catégories, indicateurs
  data_loader.py        Chargement, nettoyage, variables dérivées (mis en cache)
  filters.py            Filtres de la barre latérale, partagés entre les pages
  stats.py              IC, tests, tailles d'effet, classement des facteurs
  charts.py             Thème Plotly et fonctions de graphiques
  ui.py                 Composants d'interface (en-têtes, cartes, encadrés)
  views/                Une page par analyse
tests/                  Tests de la chaîne de données et des statistiques
data/accidents.csv      Données sources
```
