#!/usr/bin/env python3
# --------------------------------------------------------------------
# Script : wordpress_install_ubuntu24.py
# Auteur : Dimitri (avec assistance Copilot)
# Objectif :
#   Installer automatiquement WordPress sur Ubuntu 24.04
#   avec Apache2, MariaDB, PHP 8.3 et configuration sécurisée.
#
# Pourquoi ce script ?
# --------------------
# - Pour automatiser l'installation de WordPress comme tu l'as fait pour GLPI.
# - Pour éviter les erreurs manuelles.
# - Pour avoir un script réutilisable dans plusieurs années.
#
# --------------------------------------------------------------------

import os
import subprocess

# --------------------------------------------------------------------
# Fonction utilitaire : exécuter une commande shell proprement
# --------------------------------------------------------------------
def run(cmd):
    print(f"\n[+] Exécution : {cmd}")
    subprocess.run(cmd, shell=True, check=True)

# --------------------------------------------------------------------
# Mise à jour du système
# --------------------------------------------------------------------
def update_system():
    print("\n=== Mise à jour du système ===")
    run("apt update -y")
    run("apt upgrade -y")

# --------------------------------------------------------------------
# Installation Apache2 + PHP + modules nécessaires
# --------------------------------------------------------------------
def install_apache_php():
    print("\n=== Installation Apache2 + PHP 8.3 ===")
    run("apt install -y apache2")
    run("apt install -y php php-mysql php-curl php-gd php-xml php-mbstring php-zip php-intl php-soap")

# --------------------------------------------------------------------
# Installation MariaDB + sécurisation
# --------------------------------------------------------------------
def install_mariadb():
    print("\n=== Installation MariaDB ===")
    run("apt install -y mariadb-server")

    print("\n=== Sécurisation MariaDB ===")
    # Exécute le script de sécurisation interactif
    run("mysql_secure_installation")

# --------------------------------------------------------------------
# Création de la base WordPress
# --------------------------------------------------------------------
def create_database():
    print("\n=== Création de la base WordPress ===")
    print("IMPORTANT : tu devras entrer le mot de passe root MariaDB.")
    run("""mysql -u root -p -e "
        CREATE DATABASE wordpress DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        CREATE USER 'wpuser'@'localhost' IDENTIFIED BY 'MotDePasseFort123!';
        GRANT ALL PRIVILEGES ON wordpress.* TO 'wpuser'@'localhost';
        FLUSH PRIVILEGES;
    " """)

# --------------------------------------------------------------------
# Téléchargement + installation WordPress
# --------------------------------------------------------------------
def install_wordpress():
    print("\n=== Installation WordPress ===")
    run("apt install -y wget unzip")
    run("wget https://wordpress.org/latest.zip -O /tmp/wordpress.zip")
    run("unzip /tmp/wordpress.zip -d /tmp/")
    run("cp -R /tmp/wordpress/* /var/www/html/")

# --------------------------------------------------------------------
# Configuration WordPress (wp-config.php)
# --------------------------------------------------------------------
def configure_wordpress():
    print("\n=== Configuration WordPress ===")
    run("cp /var/www/html/wp-config-sample.php /var/www/html/wp-config.php")

    # Remplacement automatique des paramètres DB
    run("""sed -i "s/database_name_here/wordpress/" /var/www/html/wp-config.php""")
    run("""sed -i "s/username_here/wpuser/" /var/www/html/wp-config.php""")
    run("""sed -i "s/password_here/MotDePasseFort123!/" /var/www/html/wp-config.php""")

# --------------------------------------------------------------------
# Permissions Apache
# --------------------------------------------------------------------
def set_permissions():
    print("\n=== Permissions Apache ===")
    run("chown -R www-data:www-data /var/www/html/")
    run("chmod -R 755 /var/www/html/")

# --------------------------------------------------------------------
# Redémarrage Apache
# --------------------------------------------------------------------
def restart_apache():
    print("\n=== Redémarrage Apache ===")
    run("systemctl restart apache2")

# --------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------
if __name__ == "__main__":
    update_system()
    install_apache_php()
    install_mariadb()
    create_database()
    install_wordpress()
    configure_wordpress()
    set_permissions()
    restart_apache()

    print("\n====================================================")
    print(" WordPress est installé !")
    print(" Accès : http://ADRESSE_IP_SERVEUR")
    print("====================================================")
