# -*- coding: utf-8 -*-
"""
Contenu des fiches de révision SnowPro Core (COF-C03)
Basé sur le Guide de préparation officiel Snowflake (COF-C03, MàJ 20/02/2026)
et la documentation Snowflake publique.
"""

DOMAIN_WEIGHTS = {
    "1.0": 31,
    "2.0": 20,
    "3.0": 18,
    "4.0": 21,
    "5.0": 10,
}

DOMAIN_TITLES = {
    "1.0": "Caractéristiques et architecture de l'AI Data Cloud de Snowflake",
    "2.0": "Gestion des comptes et gouvernance des données",
    "3.0": "Chargement/Déchargement des données et connectivité",
    "4.0": "Optimisation des performances, requêtes et transformation",
    "5.0": "Collaboration sur les données",
}

DOMAIN_COLORS = {
    "1.0": "#29B5E8",  # bleu Snowflake
    "2.0": "#153860",  # bleu marine
    "3.0": "#D6246E",  # rose/magenta
    "4.0": "#FF9F36",  # orange
    "5.0": "#6ED0E0",  # cyan clair
}

DOMAIN_ICONS = {
    "1.0": "🧊",
    "2.0": "🔐",
    "3.0": "📥",
    "4.0": "⚡",
    "5.0": "🤝",
}

# Structure : DOMAINS[domain_id] = {
#   "subdomains": { "1.1": {"title":..., "content": [markdown blocks]} }
# }

DOMAINS = {
    "1.0": {
        "subdomains": {
            "1.1": {
                "title": "Décrire et utiliser l'architecture Snowflake",
                "content": """
**Architecture à trois couches, découplées et pouvant s'adapter indépendamment :**

- **Couche des services cloud (Cloud Services)** : cerveau de Snowflake. Gère l'authentification, le contrôle d'accès (RBAC), les métadonnées, l'optimiseur de requêtes, le gestionnaire de transactions, l'infrastructure de sécurité. C'est elle qui fournit le *cache de métadonnées* et gère l'*élagage* (pruning) via les métadonnées des micro-partitions.
- **Couche de calcul (Compute / Query Processing)** : les *entrepôts virtuels* (virtual warehouses), clusters MPP indépendants. Chaque entrepôt peut être démarré, arrêté et redimensionné sans impacter les autres, et sans affecter les données stockées.
- **Couche de stockage des bases de données (Storage)** : stockage columnar, compressé, organisé en micro-partitions, hébergé sur le stockage objet du cloud provider (S3, Azure Blob, GCS). Entièrement géré par Snowflake, partagé par tous les entrepôts.

**Point clé examen** : le découplage calcul/stockage permet de faire évoluer (scale up/down/out) la puissance de calcul indépendamment du volume de données stocké, et à un compte de partager les mêmes données entre plusieurs entrepôts sans duplication.

**Comparaison des éditions Snowflake** (du moins au plus complet) :
| Édition | Points clés |
|---|---|
| Standard | Fonctionnalités de base, Time Travel 1 jour |
| Enterprise | Time Travel jusqu'à 90 jours, clés de clustering multi-cluster warehouses, sécurité renforcée (row/column masking) |
| Business Critical | Chiffrement de bout en bout renforcé, HIPAA/PCI, Tri-Secret Secure, réplication/basculement pour DR |
| Virtual Private Snowflake (VPS) | Environnement isolé le plus strict, infrastructure cloud dédiée |
""",
            },
            "1.2": {
                "title": "Utiliser les interfaces et outils de Snowflake",
                "content": """
- **Snowsight** : interface Web moderne unifiée (requêtes, dashboards, Worksheets, gestion des rôles/objets, Marketplace, Cortex, Notebooks, Streamlit in Snowflake).
- **Snowflake CLI (`snow`)** : outil en ligne de commande unique remplaçant SnowSQL pour gérer objets, déployer des Native Apps, Streamlit, fonctions/procédures, et interagir avec Snowpark. (SnowSQL reste l'outil CLI historique pour l'exécution de SQL en batch/scripts.)
- **Intégrations IDE** : extensions officielles pour VS Code (et autres IDE) permettant d'écrire/exécuter du SQL, Python (Snowpark), gérer les connexions et objets directement depuis l'éditeur.

**Point clé examen** : bien distinguer Snowsight (interface web) de SnowSQL/Snowflake CLI (ligne de commande) et savoir que les connecteurs/drivers (Python, JDBC, ODBC, Node.js, Go, .NET) permettent une connectivité programmatique.
""",
            },
            "1.3": {
                "title": "Différencier la hiérarchie et les types d'objets Snowflake",
                "content": """
**Hiérarchie des conteneurs (organisation → compte → objets) :**

```
Organisation
 └── Compte(s)
      └── Base de données
           └── Schéma
                └── Objets (tables, vues, stages, UDF, procédures stockées,
                            file formats, streams, sequences, ML models, applications...)
```

**Objets d'organisation et de compte** : une *organisation* regroupe un ou plusieurs *comptes* Snowflake (souvent multi-région/multi-cloud), utile pour la gouvernance globale, le monitoring (Organization Usage) et la réplication.

**Principaux objets de base de données :**
- **Stages** : zones de préparation de fichiers (internes ou externes) utilisées pour charger/décharger des données.
- **Schémas** : conteneurs logiques regroupant tables, vues, etc. au sein d'une base.
- **Tables** : permanentes, temporaires, transitoires, externes, Apache Iceberg™, dynamiques (voir 1.5).
- **Vues** : standard, matérialisées, sécurisées (voir 1.5).
- **UDF (User-Defined Functions)** : fonctions SQL, Java, Python, Scala, JavaScript.
- **Formats de fichiers** : objets réutilisables décrivant CSV, JSON, Parquet, Avro, ORC, XML.
- **Procédures stockées** : logique procédurale (SQL scripting, Python, Java, JavaScript, Scala).
- **Canaux (Streams)** : capturent les changements (CDC) sur une table/vue.
- **Partages (Shares)** : objets permettant le Secure Data Sharing.
- **Séquences** : génération de nombres uniques.
- **Modèles de ML** : objets du Model Registry Snowflake ML.
- **Applications** : Native Apps installées depuis la Marketplace ou en interne.

**Variables de session et de contexte :**
- **Hiérarchie des paramètres** : Compte → Utilisateur → Session → Objet (les paramètres définis au niveau le plus précis l'emportent).
- **Priorité des paramètres** : un paramètre défini au niveau session prévaut sur celui du niveau utilisateur, qui prévaut lui-même sur celui du compte, etc. (du plus spécifique au plus général).
""",
            },
            "1.4": {
                "title": "Configurer des entrepôts virtuels",
                "content": """
**Types d'entrepôts virtuels :**
- **Standard (Gen 1 et Gen 2)** : Gen 2 utilise un matériel plus performant et des optimisations moteur (DML, scans de table) pour des requêtes plus rapides, à un coût par seconde plus élevé (~25-35 % selon le cloud). Gen 2 est désormais la génération par défaut là où elle est disponible.
- **Optimisé pour Snowpark (Snowpark-optimized)** : mémoire et cache plus importants par nœud, pour les charges ML/Python à forte consommation mémoire.
- **Entrepôt par défaut pour les Notebooks** : entrepôt dédié pour Snowflake Notebooks (fonctionnalité en évolution).

**Politiques d'adaptation (scaling policy)** — pour les warehouses multi-cluster :
- **Standard** : privilégie la performance, démarre un cluster supplémentaire dès qu'une requête est mise en file d'attente.
- **Économique (Economy)** : privilégie le coût, attend d'avoir suffisamment de charge avant de démarrer un cluster additionnel (au risque d'une latence plus élevée).

**Dimensionnement selon le cas d'usage :**
| Cas d'usage | Recommandation |
|---|---|
| Requêtes ad hoc / exploration | Warehouse de taille modeste, auto-suspend court |
| Chargement de données | Taille adaptée au volume de fichiers, souvent dédié |
| BI / reporting (forte concurrence) | Multi-cluster pour absorber les pics de concurrence |

**Meilleures pratiques :**
- **Dimensionnement vertical (scale up/down)** : augmente la taille (S→M→L…) pour accélérer une requête individuelle complexe (plus de nœuds de calcul par cluster).
- **Adaptation horizontale (scale out)** : ajoute des clusters (multi-cluster warehouse) pour absorber plus d'utilisateurs/requêtes concurrentes, pas pour accélérer une requête unique.
- **Suspension automatique (auto-suspend)** et **reprise automatique (auto-resume)** : réduisent les coûts en libérant le crédit dès l'inactivité.
- **Isoler les workloads** : dédier des entrepôts différents par équipe / usage (ex. ETL vs BI) pour éviter la contention de ressources et faciliter l'attribution des coûts.
""",
            },
            "1.5": {
                "title": "Expliquer les concepts de stockage Snowflake",
                "content": """
- **Micro-partitions** : unité de stockage physique immuable (~50-500 Mo de données non compressées), colonnaires, compressées automatiquement. Snowflake conserve des métadonnées (min/max, nombre de valeurs distinctes) sur chaque micro-partition pour permettre l'**élagage** (pruning) : seules les micro-partitions pertinentes sont scannées.
- **Clustering de données** : ordre physique des lignes dans les micro-partitions. Par défaut, l'ordre suit l'ordre d'ingestion (clustering naturel). Une **clé de clustering** explicite peut être définie sur de très grandes tables pour améliorer l'élagage sur les colonnes fréquemment filtrées.

**Types de table :**
| Type | Time Travel | Fail-safe | Usage |
|---|---|---|---|
| Permanente | Oui (1 à 90 j selon édition) | 7 jours | Données de production |
| Temporaire | Oui (max 1 jour) | Non | Durée de la session, données transitoires |
| Transitoire | Oui (max 1 jour) | Non | Données persistantes mais sans besoin de fail-safe (coût réduit) |
| Apache Iceberg™ | Limité | Non | Table Snowflake sur format ouvert Iceberg, catalogue interne ou externe |
| Externe | Non (métadonnées uniquement) | Non | Données restant dans un stage externe (S3, etc.), lecture seule |
| Dynamique (Dynamic Table) | Oui | Selon config | Résultat matérialisé et **rafraîchi automatiquement** d'une requête, façon déclarative de bâtir des pipelines |

**Types de vue :**
- **Standard** : requête stockée, exécutée à chaque appel, pas de stockage de résultat.
- **Matérialisée** : résultat pré-calculé et stocké, rafraîchi automatiquement par Snowflake ; utile pour accélérer des agrégations coûteuses et répétitives sur des données changeant peu.
- **Sécurisée (Secure View)** : masque la définition SQL aux utilisateurs non autorisés (utile en Data Sharing), au prix d'optimisations d'exécution parfois réduites.

**Point clé examen** : le clustering naturel n'implique aucune action de la part de l'utilisateur ; les clés de clustering explicites doivent être réservées aux tables volumineuses avec un ordre de tri qui se dégrade dans le temps.
""",
            },
            "1.6": {
                "title": "Expliquer les fonctionnalités de développement d'applications, d'IA et de ML",
                "content": """
- **Snowflake Notebooks** : environnement interactif façon Jupyter, exécuté directement sur le calcul Snowflake (SQL, Python, Markdown dans une même interface).
- **Streamlit in Snowflake** : héberger et exécuter des applications Streamlit directement dans Snowflake, sans déplacer les données, avec le contrôle d'accès RBAC natif.
- **Snowpark** : ensemble de bibliothèques et d'API (Python, Java, Scala) permettant d'écrire de la logique de traitement de données exécutée **dans** Snowflake (push-down du calcul), incluant Snowpark DataFrame API, UDF/UDTF, procédures stockées.
- **Snowflake Cortex** :
  - **Fonctions SQL d'IA** : fonctions LLM prêtes à l'emploi (résumé, traduction, complétion, classification de sentiment...) appelables directement en SQL.
  - **Cortex Search** : moteur de recherche hybride (vectoriel + lexical) pour la recherche sémantique sur des données non structurées/documents.
  - **Cortex Analyst** : permet l'interrogation en langage naturel de données structurées (text-to-SQL géré).
- **Snowflake ML** : fonctionnalités natives de Machine Learning (Feature Store, Model Registry, fonctions d'entraînement/inférence) permettant de construire et déployer des modèles sans sortir la donnée de Snowflake.

**Point clé examen** : retenir que ces fonctionnalités (Snowpark, Cortex, ML, Notebooks, Streamlit) permettent d'exécuter du code non-SQL et de l'IA **là où vit la donnée**, évitant le déplacement de données et bénéficiant de la sécurité/gouvernance native de Snowflake.
""",
            },
        }
    },
    "2.0": {
        "subdomains": {
            "2.1": {
                "title": "Expliquer le modèle et les principes de sécurité de Snowflake",
                "content": """
- **RBAC (Role-Based Access Control)** : les privilèges sont accordés à des **rôles**, et les rôles sont accordés aux utilisateurs (ou à d'autres rôles, formant une hiérarchie). Un utilisateur n'a jamais de privilège direct sur un objet.
- **DAC (Discretionary Access Control)** : chaque objet sécurisable a un **propriétaire** (rôle OWNERSHIP), qui peut accorder l'accès à cet objet à d'autres rôles. Snowflake combine RBAC (structure des rôles) et DAC (le propriétaire décide qui accède).
- **Hiérarchie des objets pouvant être sécurisés** : Compte → Base de données → Schéma → Objet ; les privilèges peuvent être hérités selon cette hiérarchie (ex : `USAGE` sur la base et le schéma nécessaires avant de pouvoir agir sur une table).
- **Politiques réseau (Network Policies)** : listes d'adresses IP autorisées/bloquées, applicables au niveau du compte ou de l'utilisateur.
- **Authentification :**
  - **MFA** (via Duo) — fortement recommandée pour tous les utilisateurs.
  - **Authentification fédérée** (SAML 2.0 avec un IdP externe type Okta, AD FS...).
  - **SSO (Single Sign-On)**.
  - **OAuth** (Snowflake OAuth ou External OAuth) — pour les intégrations d'applications tierces.
  - **Authentification par paire de clés (key-pair)** — RSA, recommandée pour les connexions programmatiques/service accounts (remplace peu à peu le mot de passe).

**Rôles :**
- **Rôles définis par le système** : `ORGADMIN`, `ACCOUNTADMIN`, `SECURITYADMIN`, `SYSADMIN`, `USERADMIN`, `PUBLIC`.
- **Rôles fonctionnels (custom)** :
  - **Rôles de comptes (account roles)** : portée sur tout le compte.
  - **Rôles de bases de données (database roles)** : portée limitée à une base de données, utile en Data Sharing pour partager des privilèges fins.
  - **Rôles personnalisés** créés selon les besoins métier.
- **Rôles secondaires** : un utilisateur peut activer plusieurs rôles secondaires en plus de son rôle principal dans une même session, cumulant ainsi leurs privilèges (utile en Snowsight).
- **Identifiants de comptes (account identifiers)** : nom de compte unique, utilisé notamment dans les URLs de connexion et pour la réplication.
- **Journalisation et traçage** : `ACCESS_HISTORY`, `LOGIN_HISTORY`, `QUERY_HISTORY` (vues du schéma `ACCOUNT_USAGE`) pour l'audit.

**Point clé examen** : hiérarchie classique des rôles système → `ACCOUNTADMIN` est au sommet (regroupe `SECURITYADMIN` + `SYSADMIN`), `SECURITYADMIN` gère utilisateurs/rôles/politiques de sécurité, `SYSADMIN` gère les objets (warehouses, DB...), `USERADMIN` crée utilisateurs et rôles.
""",
            },
            "2.2": {
                "title": "Définir les fonctionnalités de gouvernance des données et leurs modalités d'utilisation",
                "content": """
- **Masquage des données (Dynamic Data Masking)** :
  - **Sécurité au niveau des colonnes** : politiques de masquage (masking policies) appliquées à une colonne, masquant tout ou partie de la valeur selon le rôle de l'utilisateur exécutant la requête (le masquage est évalué à l'exécution, la donnée brute reste inchangée en stockage).
  - **Sécurité au niveau des lignes (Row Access Policies)** : restreint les **lignes** visibles selon le rôle/contexte de l'utilisateur.
- **Object Tagging** : étiquettes clé/valeur attachées aux objets (tables, colonnes, warehouses...), utilisées pour la classification, le suivi des coûts, ou déclencher automatiquement des politiques de masquage (tag-based masking).
- **Politiques de confidentialité (Privacy Policies / Data Classification)** : Snowflake peut classifier automatiquement les colonnes contenant des données sensibles (PII) via **Data Classification**, facilitant l'application d'Object Tagging et de masquage à grande échelle.
- **Trust Center** : tableau de bord centralisé de posture de sécurité, exécute des scanners (CIS benchmarks, etc.) et remonte des recommandations pour durcir la configuration du compte.
- **Gestion des clés de chiffrement** : chiffrement automatique **at-rest** et **in-transit**, rotation automatique des clés, hiérarchie de clés (clé racine → clés de table → clés de fichier). **Tri-Secret Secure** (Business Critical+) permet au client d'apporter sa propre clé (BYOK) combinée à la clé Snowflake.
- **Alertes** : objets programmables qui exécutent une condition (requête) et déclenchent une action si elle est vraie (souvent couplés à des notifications).
- **Notifications** : intégrations permettant d'envoyer des messages (email, cloud messaging) depuis Snowflake (tasks, alerts, erreurs de pipeline...).
- **Réplication de données et basculement (Failover)** : réplique bases de données/comptes vers une région/cloud secondaire pour la reprise après sinistre (DR) ; le **basculement** (failover) promeut la région secondaire en primaire.
- **Traçabilité des données (Data Lineage)** : suivi de l'origine et des transformations subies par la donnée (via Access History, Horizon/Data lineage graph dans Snowsight).

**Point clé examen** : le masquage dynamique agit **à la volée** (la donnée stockée n'est jamais modifiée) — c'est la différence clé avec une anonymisation physique des données.
""",
            },
            "2.3": {
                "title": "Expliquer la surveillance et la gestion des coûts",
                "content": """
- **Moniteurs de ressources (Resource Monitors)** : objets attachés à un ou plusieurs warehouses, définissant un quota de crédits sur une période. Peuvent déclencher des **actions** lorsqu'un seuil (%) est atteint : `NOTIFY`, `SUSPEND` (attend la fin des requêtes en cours) ou `SUSPEND_IMMEDIATE` (arrête tout de suite). **Les moniteurs de ressources ne consomment pas de crédits eux-mêmes** — ils ne font que surveiller/contrôler la consommation des warehouses.
- **Calcul de l'utilisation du crédit de l'entrepôt virtuel** : facturé à la seconde (minimum 60 secondes à la reprise), selon la taille du warehouse (le nombre de crédits/heure double à chaque taille : XS=1, S=2, M=4, L=8, XL=16...).
- **Schéma `ACCOUNT_USAGE`** (base `SNOWFLAKE`) : vues historiques (rétention longue, jusqu'à 1 an) sur l'usage, les requêtes, le stockage, les logins etc. À distinguer d'`INFORMATION_SCHEMA` (données quasi temps réel mais rétention courte, 7 jours à 6 mois selon la vue, et limité à la base courante).
- **Tagging du centre de coûts (Cost Center Tagging)** : associer des tags aux objets/warehouses pour ventiler les coûts par équipe/projet/centre de coût dans les rapports FinOps.
- **Budgets** : objet Snowflake permettant de définir un seuil de dépense (en $ ou crédits) sur un périmètre d'objets et de recevoir des alertes en cas de dépassement prévu — complète les Resource Monitors avec une vue plus large (au-delà des seuls warehouses).

**Point clé examen** : bien distinguer `ACCOUNT_USAGE` (historique long, léger différé, vue compte entier) vs `INFORMATION_SCHEMA` (temps quasi réel, rétention courte, portée limitée à la base de données courante).
""",
            },
        }
    },
    "3.0": {
        "subdomains": {
            "3.1": {
                "title": "Effectuer le chargement et le déchargement des données",
                "content": """
- **Formats de fichiers supportés** : CSV/délimité, JSON, Avro, ORC, Parquet, XML (structurés et semi-structurés).
- **Zones de préparation (Stages)** :
  - **Internes** : stockage géré par Snowflake — stage utilisateur (`@~`), stage de table (`@%table`), stage nommé interne.
  - **Externes** : pointent vers un bucket/conteneur cloud existant (S3, Azure Blob, GCS) via une **intégration de stockage** (storage integration), méthode recommandée car elle évite de stocker des identifiants cloud dans Snowflake.
  - **Chiffrement côté serveur (SSE)** : chiffrement géré par le cloud provider pour les stages externes (vs chiffrement côté client).
  - **Tables de répertoire (Directory Tables)** : métadonnées catalographiques (nom de fichier, taille, URL...) sur les fichiers d'un stage, interrogeables en SQL — utile notamment pour les données non structurées.
- **Commande `COPY INTO`** :
  - `COPY INTO <table>` : charge les données d'un stage vers une table.
  - `COPY INTO <location>` : décharge (exporte) les données d'une table vers un stage.
  - S'appuie sur l'objet `FILE FORMAT` et gère la déduplication automatique des fichiers déjà chargés (via les métadonnées de charge, 64 derniers jours).
- **Options de gestion des erreurs (`ON_ERROR`)** : `CONTINUE` (ignore les lignes en erreur), `SKIP_FILE` (ignore le fichier entier dès la 1ère erreur), `SKIP_FILE_<n>` / `SKIP_FILE_<n>%` (seuil), `ABORT_STATEMENT` (par défaut, arrête tout au 1er problème).

**Point clé examen** : `COPY INTO` ne recharge pas un fichier déjà chargé avec succès (sauf `FORCE=TRUE`) — mécanisme clé pour éviter les doublons lors de charges répétées.
""",
            },
            "3.2": {
                "title": "Effectuer l'ingestion automatisée des données",
                "content": """
- **Snowpipe** : ingestion **continue** quasi temps réel, déclenchée par notification d'événement cloud (ex : nouvel objet S3) ou appel REST, facturée à l'usage (par charge, pas de warehouse dédié à gérer manuellement) — idéale pour des fichiers arrivant en flux.
- **Snowpipe Streaming** : API bas niveau permettant d'insérer des lignes **directement** (sans écrire de fichier au préalable), avec une latence de l'ordre de la seconde — pour les flux à très faible latence (Kafka, applications).
- **Streams** : objet capturant les changements (insert/update/delete = **CDC**, Change Data Capture) sur une table/vue source depuis le dernier point de consommation (offset), sans dupliquer les données (metadata uniquement : `METADATA$ACTION`, `METADATA$ISUPDATE`, `METADATA$ROW_ID`).
- **Tasks** : planificateur de requêtes SQL (ou appel de procédure stockée), déclenché par un **cron** (`SCHEDULE`) ou en chaîne (`AFTER <task>` pour former un **DAG**). Un Task combiné à un Stream permet un traitement **incrémental** automatisé (le Task ne s'exécute que si le Stream contient des données, via `WHEN SYSTEM$STREAM_HAS_DATA(...)`).
- **Dynamic Tables** : déclaratif — on écrit la requête cible (le "quoi"), Snowflake gère automatiquement le rafraîchissement incrémental (le "comment"), selon un `TARGET_LAG` défini, en s'appuyant en interne sur un mécanisme proche des Streams/Tasks mais sans les gérer manuellement.
- **Openflow** *(fonctionnalité en cours de déploiement)* : service d'intégration/ingestion de données géré par Snowflake, basé sur Apache NiFi, pour construire des pipelines d'ingestion sans code vers Snowflake.

**Point clé examen** : bien différencier Snowpipe (fichiers, event-driven) de Snowpipe Streaming (lignes, sans fichier, très faible latence) ; et retenir que **Streams + Tasks = traitement incrémental orchestré manuellement**, alors que **Dynamic Tables = équivalent déclaratif et automatisé**.
""",
            },
            "3.3": {
                "title": "Identifier les différents connecteurs et intégrations Snowflake",
                "content": """
- **Pilotes (drivers) Snowflake** : JDBC, ODBC, Python Connector, Node.js, Go, .NET — permettent la connexion programmatique depuis des applications/langages tiers.
- **Connecteurs Snowflake** : intégrations prêtes à l'emploi avec des outils tiers, ex. **Connecteur Kafka**, **Connecteur Spark**, connecteurs BI (Tableau, Power BI...).
- **Intégration de stockage (Storage Integration)** : objet Snowflake stockant une identité cloud (IAM Role AWS, Service Principal Azure...) permettant d'accéder à un stage externe **sans** exposer de clés d'accès directement dans Snowflake — méthode recommandée pour sécuriser l'accès aux stages externes.
- **Intégration d'API (API Integration)** : objet définissant les identifiants/permissions nécessaires pour appeler des services externes, utilisé par les External Functions, Snowpipe (notifications) et External Network Access.
- **Intégration Git** : connexion directe d'un dépôt Git (GitHub, GitLab, Azure DevOps...) à Snowflake permettant d'exécuter des scripts/objets versionnés directement depuis le dépôt (utile pour les workflows CI/CD et Native Apps).

**Point clé examen** : une **Storage Integration** évite de stocker des clés d'accès cloud (secrets) dans Snowflake — c'est la bonne pratique de sécurité à privilégier pour les stages externes.
""",
            },
        }
    },
    "4.0": {
        "subdomains": {
            "4.1": {
                "title": "Évaluer les performances des requêtes",
                "content": """
- **Query Profile** : représentation graphique de l'exécution d'une requête (opérateurs, temps passé), essentielle pour diagnostiquer les problèmes de performance. Signaux clés à surveiller :
  - **Octets déversés sur le stockage (spilling)** : la requête manque de mémoire et déverse des données temporaires sur disque local, voire sur le stockage distant (remote spilling, encore plus lent) → souvent résolu en augmentant la taille du warehouse.
  - **Élagage inefficace (pruning)** : trop de micro-partitions scannées par rapport au nécessaire → revoir les filtres/la clé de clustering.
  - **Explosion de jointures (join explosion)** : une jointure produit beaucoup plus de lignes que prévu (cardinalités mal maîtrisées) → revoir les clés/conditions de jointure.
  - **Mise en file d'attente (queuing)** : requêtes en attente faute de ressources disponibles sur le warehouse → warehouse trop petit / trop sollicité, envisager le multi-cluster ou l'isolement des workloads.
- **Vues `SNOWFLAKE.ACCOUNT_USAGE`** :
  - **Attribution des requêtes (Query Attribution History)** : ventile le coût/la consommation par requête.
  - **Historique des requêtes (`QUERY_HISTORY`)** : détail de toutes les requêtes exécutées (durée, warehouse, utilisateur, statut, bytes scannés...).
- **Meilleures pratiques de gestion des workloads** : regrouper les charges de travail similaires (même profil de requêtes/concurrence) sur un même warehouse dédié, pour optimiser le cache et éviter la contention entre profils très différents (ETL vs BI vs ad hoc).
""",
            },
            "4.2": {
                "title": "Optimiser les performances des requêtes",
                "content": """
- **Query Acceleration Service (QAS)** : décharge dynamiquement une partie du traitement d'une requête (scans/filtres volumineux) vers une infrastructure de calcul serverless additionnelle, en particulier utile pour les requêtes ad hoc avec des pics de charge imprévisibles (activé par défaut sur les nouveaux warehouses Gen2).
- **Search Optimization Service (SOS)** : maintient une structure de recherche additionnelle pour accélérer les requêtes de type **recherche ponctuelle** (point lookup, égalité, `IN`, parfois `LIKE`/substring) sur des colonnes à forte cardinalité qui ne bénéficieraient pas naturellement de l'élagage classique.
- **Clés de clustering** : réorganisent physiquement les données pour améliorer l'élagage sur les colonnes fréquemment filtrées/jointes ; à réserver aux **très grandes tables** (multi-To) dont l'ordre naturel se dégrade avec le temps (DML fréquents).
- **Vues matérialisées** : pré-calculent et stockent le résultat d'une requête (souvent une agrégation), rafraîchies automatiquement par Snowflake ; utiles quand la même requête coûteuse est exécutée fréquemment sur des données changeant peu.

**Point clé examen** : QAS accélère le **scan/filtrage** d'une requête individuelle volumineuse ; SOS accélère les **recherches ponctuelles** répétées ; les clés de clustering et vues matérialisées sont des optimisations plus **structurelles**, à mettre en place quand un pattern de requêtes est récurrent et prévisible.
""",
            },
            "4.3": {
                "title": "Utiliser la mise en cache de Snowflake",
                "content": """
Snowflake dispose de **3 niveaux de cache** :

1. **Cache de résultats de requêtes (Result Cache)** : stocké au niveau de la couche Cloud Services, conserve le résultat d'une requête pendant 24 heures (prolongeable jusqu'à 31 jours si régulièrement réutilisé). Réutilisé si la requête est **strictement identique** (texte identique) et que les données sous-jacentes n'ont pas changé — **aucun warehouse n'est nécessaire** pour servir un résultat depuis ce cache (coût quasi nul).
2. **Cache de métadonnées (Metadata Cache)** : géré par la couche Cloud Services, contient les statistiques sur les micro-partitions (min/max, nb lignes...) utilisées pour l'élagage et certaines requêtes purement sur métadonnées (ex : `COUNT(*)` sans filtre) peuvent être servies sans warehouse actif.
3. **Cache d'entrepôts (Warehouse / Local Disk Cache)** : propre à chaque cluster de calcul, met en cache localement (SSD) les données lues depuis le stockage distant lors des requêtes précédentes. **Perdu à la suspension du warehouse** — c'est pourquoi un auto-suspend trop agressif peut nuire à la performance en réchauffant le cache trop souvent.

**Point clé examen** : le cache de résultats de requêtes est le seul qui ne nécessite **aucun warehouse actif**. Le cache d'entrepôts est vidé dès la suspension du warehouse.
""",
            },
            "4.4": {
                "title": "Utiliser des techniques de transformation des données",
                "content": """
**Transformation à partir de différents types de données :**
- **Structurées** : SQL standard (SELECT, JOIN, GROUP BY...).
- **Semi-structurées** (JSON, Avro, ORC, Parquet, XML) : type `VARIANT`, notation `:` pour naviguer (`payload:customer.name`), fonctions `FLATTEN`, `PARSE_JSON`, `OBJECT_CONSTRUCT`, `ARRAY_AGG`...
- **Non structurées** (images, PDF, audio...) : gérées via des types `FILE`, des Directory Tables et des fonctions dédiées (souvent combinées à Cortex/UDFs Python pour l'extraction/l'analyse).

**Fonctions d'agrégation** : `SUM`, `AVG`, `COUNT`, `MIN`, `MAX`, mais aussi des agrégations semi-structurées (`ARRAY_AGG`, `OBJECT_AGG`), et des extensions analytiques comme `GROUP BY ROLLUP`/`CUBE`.

**Application du langage SQL pour optimiser les requêtes** : privilégier le filtrage précoce (predicate pushdown naturel), limiter les `SELECT *`, éviter les fonctions non-déterministes bloquant l'élagage sur les colonnes filtrées, exploiter les CTE pour la lisibilité (sans surestimer leur impact perf, Snowflake les optimise généralement comme des vues en ligne).

**Fonctions de fenêtre (Window Functions)** : `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LAG()`/`LEAD()`, agrégats avec `OVER (PARTITION BY ... ORDER BY ...)` — permettent des calculs sur un ensemble de lignes liées à la ligne courante sans `GROUP BY` (pas de perte de granularité).

**Point clé examen** : `VARIANT` est le type clé pour stocker et interroger nativement du semi-structuré ; `FLATTEN` est la fonction de table permettant d' "aplatir" des tableaux/objets imbriqués en lignes.
""",
            },
        }
    },
    "5.0": {
        "subdomains": {
            "5.1": {
                "title": "Expliquer la collaboration sur les données et la protection des données",
                "content": """
- **Réplication de données et basculement** : réplique des objets (comptes, bases de données) vers une région/cloud secondaire ; le **basculement (failover)** bascule le rôle primaire vers la région secondaire en cas d'indisponibilité — pilier de la continuité d'activité (DR).
- **Fonctionnalités de Secure Data Sharing** : permet de partager des données **en lecture seule**, **sans copie ni mouvement physique** des données, entre comptes Snowflake (voir 5.2).
- **Clonage (Zero-Copy Cloning)** : crée une copie instantanée d'une base/schéma/table via des métadonnées uniquement (pas de duplication physique immédiate) ; les modifications ultérieures sur l'original ou le clone créent de nouvelles micro-partitions propres à chacun (copy-on-write) — utile pour créer rapidement des environnements de test/dev à coût quasi nul au moment du clonage.
- **Time Travel** : permet d'interroger, restaurer (`UNDROP`) ou cloner l'état d'un objet à un instant passé (`AT`/`BEFORE`), pendant une période configurable (0 à 1 jour en Standard, jusqu'à 90 jours en Enterprise+).
- **Fail-safe** : période supplémentaire de **7 jours non configurable**, après expiration du Time Travel, pendant laquelle **seul Snowflake** peut restaurer les données (via un contact support) en cas de sinistre majeur — ce n'est pas un mécanisme en libre-service pour l'utilisateur.

**Point clé examen** : Time Travel = en libre-service, durée configurable, disponible pour requêtes/restauration/clonage. Fail-safe = filet de sécurité, 7 jours fixes, uniquement via le support Snowflake.
""",
            },
            "5.2": {
                "title": "Expliquer les capacités de partage de données de Snowflake",
                "content": """
**Types de comptes dans le partage :**
- **Compte fournisseur (provider)** : possède les données et les partage.
- **Compte utilisateur/consommateur (consumer)** : compte Snowflake existant qui consomme le partage.
- **Comptes lecteurs (Reader Accounts)** : comptes Snowflake **gérés et payés par le fournisseur**, créés pour des consommateurs qui n'ont pas eux-mêmes de compte Snowflake — ils peuvent uniquement lire les données partagées, sans capacité de calcul propre indépendante.

- **Secure Data Sharing** : partage natif Snowflake, **sans copie physique** des données — le consommateur interroge directement les données du fournisseur avec son propre compute, en lecture seule et en temps réel.
- **Partage et nouveau partage (Share / Re-share)** : un partage repose sur un objet **Share** listant bases/schémas/objets accordés ; un consommateur autorisé peut, selon les droits accordés, re-partager (re-share) des données reçues avec d'autres comptes.
- **Direct Shares** : partage point à point direct entre un fournisseur et un ou plusieurs consommateurs nommés (sans passer par un Listing public de la Marketplace).
- **Data Clean Rooms** : environnement collaboratif permettant à deux parties d'analyser des données combinées (souvent sensibles, ex. marketing) **sans qu'aucune des deux ne voie les données brutes de l'autre** — les règles/politiques d'accès contrôlent ce qui peut être calculé et restitué.
""",
            },
            "5.3": {
                "title": "Partager des données à l'aide de la Marketplace Snowflake et des références",
                "content": """
- **Marketplace Snowflake (Snowflake Marketplace)** : place de marché où des fournisseurs publient des jeux de données/applications consommables directement (sans ETL) par tout compte Snowflake, avec parfois facturation associée.
- **Listings** :
  - **Privées (Private Listings)** : visibles uniquement par les comptes consommateurs explicitement invités — équivalent d'un Direct Share packagé avec le cycle de vie d'un Listing (versioning, mises à jour...).
  - **Publiques (Public Listings)** : visibles par tous les comptes Snowflake sur la Marketplace.
- **Native Apps (Snowflake Native App Framework)** : permet de packager de la logique applicative (code + UI, ex. via Streamlit) et de la distribuer via la Marketplace ou un partage privé ; l'application **s'exécute dans le compte du consommateur**, sur son propre compute, tout en protégeant la propriété intellectuelle du code du fournisseur (le consommateur ne voit pas le code source, seulement l'application).

**Point clé examen** : bien distinguer un **Share classique** (données brutes accessibles en lecture) d'une **Native App** (logique + UI exécutées côté consommateur, code protégé) — la Native App va au-delà du simple partage de données.
""",
            },
        }
    },
}