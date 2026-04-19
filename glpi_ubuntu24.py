#!/usr/bin/env python3

import os
import re
import subprocess
import getpass

mysql_password = None  # Initialisation de la variable globale mysql_password

def run_command(command):
    """Exécute une commande shell et arrête le script en cas d'erreur."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Command failed: {result.stderr}")
        exit(1)
    return result.stdout

def install_dependencies():
    """Installe les dépendances compatibles Ubuntu 24.04 (PHP 8.3)."""
    packages = [
        'python3-pip', 'mariadb-server', 'apache2', 'php', 'libapache2-mod-php',
        'php-imap', 'php-ldap', 'php-curl', 'php-gd', 'php-mysql',
        'php-xml', 'php-intl', 'php-apcu', 'apcupsd'
    ]

    run_command("sudo apt-get update")
    run_command("sudo apt-get upgrade -y")
    run_command("sudo apt-get install -y " + " ".join(packages))

def install_mysql_connector_python():
    """Installe le connecteur MySQL Python."""
    try:
        subprocess.run(["sudo", "pip3", "install", "mysql-connector-python"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install mysql-connector-python. Error: {e.stderr}")
        exit(1)

def check_and_install_mysql_connector_python():
    """Vérifie si mysql.connector est installé, sinon l'installe."""
    try:
        import mysql.connector
    except ImportError:
        install_mysql_connector_python()

def fix_broken_dependencies():
    """Répare les dépendances cassées."""
    run_command("sudo apt --fix-broken install")

def install_mariadb():
    """Installe MariaDB."""
    run_command("sudo apt-get install -y mariadb-server python3")

def set_mysql_password():
    """Demande un mot de passe MySQL et configure la base GLPI."""
    global mysql_password

    if mysql_password is not None:
        return

    while True:
        mysql_password = getpass.getpass("Enter a strong MySQL password: ")
        confirm_password = getpass.getpass("Confirm the password: ")

        if mysql_password == confirm_password and (
            len(mysql_password) >= 8
            and re.search(r"\d", mysql_password)
            and re.search(r"[a-z]", mysql_password)
            and re.search(r"[A-Z]", mysql_password)
            and re.search(r"[!@#$%^&*()\-_=+{};:,<.>]", mysql_password)
        ):
            break
        else:
            print("Password invalid. Try again.")

    run_command("sudo mysql -e 'DROP DATABASE IF EXISTS glpidb;'")
    run_command("sudo mysql -e 'CREATE DATABASE glpidb;'")
    run_command(f"sudo mysql -e \"GRANT ALL PRIVILEGES ON glpidb.* TO 'glpiuser'@'localhost' IDENTIFIED BY '{mysql_password}';\"")

def download_glpi():
    """Télécharge et installe GLPI."""
    glpi_url = "https://github.com/glpi-project/glpi/releases/download/10.0.7/glpi-10.0.7.tgz"
    run_command(f"wget {glpi_url}")
    run_command("tar -xvzf glpi-10.0.7.tgz -C /var/www/html")
    run_command("sudo chown -R www-data:www-data /var/www/html/glpi/")

def configure_glpi():
    """Configure GLPI (config.php)."""
    config_file = "/var/www/html/glpi/config/config.php"

    config_content = f"""<?php
class DB extends DBmysql {{
   public $dbhost = 'localhost';
   public $dbuser = 'glpiuser';
   public $dbpassword = '{mysql_password}';
   public $dbdefault = 'glpidb';
   public $use_utf8mb4 = true;
   public $allow_myisam = false;
   public $allow_datetime = false;
   public $allow_signed_keys = false;
}}
"""

    with open(config_file, "w") as f:
        f.write(config_content)

    run_command("sudo systemctl restart apache2")

def configure_config_db_php():
    """Configure config_db.php."""
    config_db_file = "/var/www/html/glpi/config/config_db.php"

    config_db_content = f"""<?php
class DB extends DBmysql {{
   public $dbhost = 'localhost';
   public $dbuser = 'glpiuser';
   public $dbpassword = '{mysql_password}';
   public $dbdefault = 'glpidb';
   public $use_utf8mb4 = true;
   public $allow_myisam = false;
   public $allow_datetime = false;
   public $allow_signed_keys = false;
}}
"""

    with open(config_db_file, "w") as f:
        f.write(config_db_content)

    run_command(f"sudo chown www-data:www-data {config_db_file}")
    run_command("sudo systemctl restart apache2")

def configure_virtualhost():
    """Configure le VirtualHost Apache."""
    server_admin = input("Enter ServerAdmin email: ")
    server_name = input("Enter ServerName (ex: glpi.local): ")

    virtualhost_config = f"""
<VirtualHost *:80>
    ServerAdmin {server_admin}
    DocumentRoot /var/www/html/glpi/
    ServerName {server_name}

    <Directory /var/www/html/glpi/>
        Options FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${{APACHE_LOG_DIR}}/error.log
    CustomLog ${{APACHE_LOG_DIR}}/access.log combined
</VirtualHost>
"""

    with open("/etc/apache2/sites-available/glpi.conf", "w") as f:
        f.write(virtualhost_config)

    run_command("sudo a2ensite glpi.conf")
    run_command("sudo systemctl reload apache2")

def import_sql_file():
    """Importe la sauvegarde SQL."""
    mysql_user = "glpiuser"
    mysql_password = getpass.getpass(f"Enter MySQL password for '{mysql_user}': ")

    command = f"mysql -u {mysql_user} -p{mysql_password} glpidb < glpi_backup.sql"

    try:
        subprocess.run(command, shell=True, check=True)
        print("SQL import successful.")
    except subprocess.CalledProcessError as e:
        print(f"SQL import failed: {e.stderr}")
        exit(1)

def main():
    try:
        fix_broken_dependencies()
        install_dependencies()
        install_mysql_connector_python()
        check_and_install_mysql_connector_python()
        install_mariadb()
        set_mysql_password()
        download_glpi()
        configure_glpi()
        configure_config_db_php()
        configure_virtualhost()
        import_sql_file()
        run_command("sudo rm -fR /var/www/html/glpi/install")

        print("GLPI installation completed successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()