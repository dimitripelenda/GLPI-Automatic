# GLPI-Automatic
Projet pour automatiser installation glpi 

# Présentation du projet :
Le projet GLPI (Gestionnaire Libre de Parc Informatique) est un système de gestion de parc informatique et de service d'assistance. Il offre une plateforme complète pour la gestion des ressources matérielles et logicielles, la gestion des incidents, la gestion des demandes de service et bien plus encore. GLPI est utilisé par de nombreuses organisations pour améliorer l'efficacité de leur parc informatique et assurer un support informatique de qualité.

# Objectifs du projet
Le principal objectif du projet GLPI est de fournir aux organisations un outil centralisé et complet pour gérer leur parc informatique. Il vise à simplifier les tâches de gestion des actifs matériels et logiciels, de suivi des incidents, de gestion des changements, de gestion des licences et de gestion des contrats. L'objectif est d'améliorer l'efficacité opérationnelle, de réduire les coûts liés à la maintenance et d'offrir un support informatique de qualité aux utilisateurs.

# Contexte
Dans un environnement informatique en constante évolution, il est essentiel pour les organisations de disposer d'un système de gestion efficace pour leur parc informatique. Avec la croissance du nombre d'actifs informatiques, il devient de plus en plus difficile de suivre, maintenir et résoudre les problèmes liés à ces actifs de manière manuelle. GLPI offre une solution automatisée qui permet de centraliser et de rationaliser les processus de gestion du parc informatique.

# Importance du projet
La gestion efficace du parc informatique est essentielle pour assurer la disponibilité, la fiabilité et la sécurité des ressources informatiques au sein d'une organisation. Un système comme GLPI permet aux équipes informatiques de disposer d'une vision claire sur les actifs informatiques, les contrats, les incidents et les demandes de service. Cela facilite la prise de décision, la planification des ressources et l'amélioration continue des services informatiques. GLPI contribue ainsi à optimiser les opérations informatiques et à garantir une meilleure satisfaction des utilisateurs.

# 1. Installation des paquets requis

sudo apt-get update
sudo apt-get install apache2 php libapache2-mod-php php-imap php-ldap php-curl php-xmlrpc php-gd php-mysql php-cas php8.1-mysqli php8.1-dom php8.1-xml php8.1-curl php8.1-gd php8.1-intl -y
Installer apcupsd et php-apcu :
sudo apt-get install apcupsd php-apcu -y

Redémarrer Apache :
sudo systemctl restart apache2

# 2. Installation de MariaDB et configuration de la base de données
sudo apt-get install mariadb-server -y

Créer la base de données et accorder les privilèges :

sudo mysql -e "CREATE DATABASE glpidb;"

sudo mysql -e "GRANT ALL PRIVILEGES ON glpidb.* TO glpiuser@localhost IDENTIFIED BY 'eder';"

sudo mysql -e "EXIT"

# 3. Téléchargement et installation de GLPI
wget https://github.com/glpi-project/glpi/releases/download/10.0.7/glpi-10.0.7.tgz

tar -xvzf glpi-10.0.7.tgz -C /var/www/html

sudo chown -R www-data /var/www/html/glpi/

# 4. Vérification de l'installation
if os.path.exists("/var/www/html/glpi/index.php"):
    print("L'installation de GLPI s'est terminée avec succès.")
else:
    print("Une erreur s'est produite lors de l'installation de GLPI.")

# Exécuter un script Python
Création de fichier Python
touch glpiScript.py

Exécuter un script Python
Après avoir copié le script, rendez le script exécutable à l'aide de la commande suivante :

chmod +x glpiScript.py

exécutez ce script comme ci-dessous :

./glpiScript.py
