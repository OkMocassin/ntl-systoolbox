# NTL System Toolbox

**NTL-SysToolbox** est un utilitaire en ligne de commande (CLI) développé en Python 3.9+ conçu pour industrialiser l'exploitation de l'infrastructure de **Nord Transit Logistics (NTL)**. Il centralise le diagnostic des services, la sécurisation des sauvegardes métier et l'audit d'obsolescence du parc informatique.

##  Fonctionnalités principales

L'outil s'articule autour de trois modules indépendants[cite: 65]:

**Module Diagnostic** : Vérification des services Active Directory/DNS, test de santé de la base MySQL du WMS et monitoring des ressources système (CPU, RAM, Disque)[cite: 67, 68].
**Module Backup** : Sauvegardes complètes via `mysqldump`, export de tables en CSV et gestion automatique de la rétention des fichiers[cite: 70, 71, 72].
**Module Audit** : Scan réseau pour l'inventaire des composants, identification des systèmes d'exploitation et rapport de conformité basé sur les dates de fin de vie (EOL)[cite: 74, 77].

##  Prérequis

**Systèmes d'exploitation** : Windows Server 2016+, Windows 10/11 ou Ubuntu 18.04+, Debian 10+, CentOS/RHEL 7+[cite: 228, 229].
**Langage** : Python 3.9 ou supérieur[cite: 229].
* **Outils tiers** :
    **Nmap** (optionnel) : Recommandé pour la détection avancée des OS[cite: 229].
    **MySQL Client** : Requis pour les fonctions de sauvegarde[cite: 230].

