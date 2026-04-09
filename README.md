# NTL System Toolbox

**NTL-SysToolbox** est un utilitaire en ligne de commande (CLI) développé en Python 3.9+ conçu pour industrialiser l'exploitation de l'infrastructure de **Nord Transit Logistics (NTL)**. Il centralise le diagnostic des services, la sécurisation des sauvegardes métier et l'audit d'obsolescence du parc informatique.

##  Fonctionnalités principales

L'outil s'articule autour de trois modules indépendants:

### **Module Diagnostic** : 

Vérification des services Active Directory/DNS,

Test de santé de la base MySQL du WMS

Monitoring des ressources système (CPU, RAM, Disque).



### **Module Backup** : 

Sauvegardes complètes via `mysqldump`,

Export de tables en CSV 

Gestion automatique de la rétention des fichiers.



### **Module Audit** : 

Scan réseau pour l'inventaire des composants, 

Identification des systèmes d'exploitation 

Rapport de conformité basé sur les dates de fin de vie (EOL).




##  Prérequis

**Systèmes d'exploitation** : Windows Server 2016+, Windows 10/11 ou Ubuntu 18.04+, Debian 10+, CentOS/RHEL 7+.

**Langage** : Python 3.9 ou supérieur.



