# Automatisation de l'installation et configuration de GLPI à partir de la machine vierge

## Automatisation de GLPI en 3 minutes !
Bienvenue dans le projet d'automatisation de GLPI en un temps record ! Si vous êtes passionné par la gestion de votre parc informatique avec GLPI, vous savez à quel point cette application est puissante. Cependant, l'installation et la configuration peuvent parfois être longues et fastidieuses. C'est là que notre script entre en jeu pour vous faire gagner du temps !

## L'objectif en quelques minutes
L'objectif principal de ce projet est simple : rendre l'installation et la configuration de GLPI plus rapides que jamais. En utilisant notre script install_glpi.py, vous pouvez obtenir un GLPI entièrement fonctionnel en seulement 3 minutes ! Cela signifie que vous serez opérationnel en un clin d'œil, sans vous soucier des étapes manuelles complexes.

## Pourquoi cette automatisation est géniale
Imaginez : au lieu de passer du temps à naviguer dans des tutoriels, à configurer manuellement des paquets et à répondre à de nombreuses questions, vous pouvez simplement exécuter notre script et tout cela sera fait pour vous. En 3 minutes, vous aurez un GLPI prêt à l'emploi, proprement configuré et prêt à être utilisé.

## Prérequis
Pour profiter de cette installation ultrarapide, assurez-vous de répondre aux prérequis suivants :

1. Système Linux Ubuntu: Ce script est conçu pour fonctionner spécifiquement sur un système Linux Ubuntu.

2. Accès root: Vous aurez besoin d'accès administratif (accès root) pour exécuter certaines commandes système.

## Instructions d'utilisation
Téléchargement du script: Téléchargez simplement le fichier install_glpi.py sur votre système.

## Exécution du script: Ouvrez un terminal et exécutez le script en utilisant la commande suivante :
python3 glpi_automated.py ou ./glpi_automated.py

Assurez-vous d'utiliser cette commande avec des privilèges administratifs.

## Suivez les instructions:
Le script vous guidera tout au long du processus. Il vous posera des questions simples auxquelles vous devrez répondre pour personnaliser votre installation.

## Finalisation: 
Une fois le script terminé, GLPI sera opérationnel sur votre système. Vérifiez le résultat en accédant à l'interface web de GLPI à l'adresse que vous avez fournie lors de l'exécution du script (par exemple : http://votre-adresse-ip-ou-domaine/glpi).

## Avertissement
Assurez-vous de sauvegarder vos données importantes avant d'exécuter le script, car il peut modifier la configuration de votre système. Ce script est conçu pour automatiser le processus d'installation, ce qui signifie qu'il peut affecter les configurations existantes.

# Pour exécution du script Python
Par example: Création de fichier Python
touch glpi_automated.py

Exécuter un script Python
Après avoir copié le script, rendez le script exécutable à l'aide de la commande suivante :

chmod +x glpi_automated.py

exécutez ce script comme ci-dessous : 
Notez bien le script doit etre dans le meme repertoire que le fichier sql: glpi_backup.sql
python glpi_automated.py ou ./glpi_automated.py

# Connexion sur l'interface Web
### login par defaut: glpi
### password par defaut : glpi
# Notez bien , il est conseillé de changer password et login par defaut ! 






