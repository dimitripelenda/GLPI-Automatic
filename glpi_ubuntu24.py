#!/usr/bin/env python3

import os
import re
import subprocess
import getpass

mysql_password = None  # Initialisation de la variable globale mysql_password

def run_command(command):
    """Exécute une commande shell et arrête le script en cas d'erreur."""
    print(f"[RUN] {command}")
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {result.stderr}")
        exit(1)
    return result.stdout

def install_dependencies():
    """Installe les dépendances compatibles Ubuntu 24.04 (PHP 8.3)."""
    packages = [
        'mariadb-server', 'apache2', 'php', 'libapache2-mod-php',
        'php-imap', 'php-ldap', 'php-curl', 'php-gd', 'php-mysql',
        'php-xml', 'php-intl', 'php-apcu', 'apcupsd',
        'python3-mysql.connector'
    ]

    run_command("sudo apt-get update")
    run_command("sudo apt-get upgrade -y")
    run_command("sudo apt-get install -y " + " ".join(packages))

def check_and_install_mysql_connector_python():
    """Vérifie si mysql.connector est installé, sinon l'installe via APT (compatible Ubuntu 24.04)."""
    try:
        import mysql.connector  # noqa: F401
        print("[INFO] mysql.connector déjà installé.")
    except ImportError:
        print("[INFO] mysql.connector non installé. Installation via APT...")
        run_command("sudo apt-get install -y python3-mysql.connector")

def fix_broken_dependencies():
    """Répare les dépendances cassées."""
    run_command("sudo apt --fix-broken install -y")

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
            and re.search(r"[!@#$%^&*()\\-_=+{};:,<.>]", mysql_password)
        ):
            break
        else:
            print("Password invalid. Try again (min 8 chars, upper, lower, digit, special).")

    print("[INFO] Configuration de la base MariaDB pour GLPI...")
    run_command("sudo systemctl enable mariadb")
    run_command("sudo systemctl start mariadb")

    run_command("sudo mysql -e 'DROP DATABASE IF EXISTS glpidb;'")
    run_command("sudo mysql -e 'CREATE DATABASE glpidb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'")
    run_command(
        f"sudo mysql -e \"CREATE USER IF NOT EXISTS 'glpiuser'@'localhost' IDENTIFIED BY '{mysql_password}';\""
    )
    run_command(
        "sudo mysql -e \"GRANT ALL PRIVILEGES ON glpidb.* TO 'glpiuser'@'localhost'; FLUSH PRIVILEGES;\""
    )

def download_glpi():
    """Télécharge et installe GLPI."""
    glpi_url = "https://github.com/glpi-project/glpi/releases/download/10.0.7/glpi-10.0.7.tgz"

    print("[INFO] Création du répertoire /var/www/html si nécessaire...")
    run_command("sudo mkdir -p /var/www/html")

    print("[INFO] Téléchargement de GLPI...")
    run_command(f"wget -O /tmp/glpi-10.0.7.tgz {glpi_url}")

    print("[INFO] Extraction de GLPI dans /var/www/html ...")
    run_command("sudo tar -xvzf /tmp/glpi-10.0.7.tgz -C /var/www/html")

    print("[INFO] Droits sur /var/www/html/glpi ...")
    run_command("sudo chown -R www-data:www-data /var/www/html/glpi/")
    run_command("sudo chmod -R 755 /var/www/html/glpi/")

def configure_glpi():
    """Configure GLPI (config.php)."""
    config_dir = "/var/www/html/glpi/config"
    config_file = os.path.join(config_dir, "config.php")

    if not os.path.isdir(config_dir):
        print(f"[ERROR] Le répertoire {config_dir} n'existe pas. GLPI est-il bien extrait ?")
        exit(1)

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

    print("[INFO] Écriture de config.php...")
    with open(config_file, "w") as f:
        f.write(config_content)

    run_command(f"sudo chown www-data:www-data {config_file}")
    run_command("sudo systemctl restart apache2")

def configure_config_db_php():
    """Configure config_db.php."""
    config_dir = "/var/www/html/glpi/config"
    config_db_file = os.path.join(config_dir, "config_db.php")

    if not os.path.isdir(config_dir):
        print(f"[ERROR] Le répertoire {config_dir} n'existe pas. GLPI est-il bien extrait ?")
        exit(1)

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

    print("[INFO] Écriture de config_db.php...")
    with open(config_db_file, "w") as f:
        f.write(config_db_content)

    run_command(f"sudo chown www-data:www-data {config_db_file}")
    run_command("sudo systemctl restart apache2")

def configure_virtualhost():
    """Configure le VirtualHost Apache."""
    print("[INFO] Configuration du VirtualHost Apache pour GLPI...")
    server_admin = input("Enter ServerAdmin email (ex: admin@example.com): ").strip() or "admin@example.com"
    server_name = input("Enter ServerName (ex: glpi.local): ").strip() or "glpi.local"

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

    ErrorLog ${{APACHE_LOG_DIR}}/glpi_error.log
    CustomLog ${{APACHE_LOG_DIR}}/glpi_access.log combined
</VirtualHost>
"""

    with open("/tmp/glpi.conf", "w") as f:
        f.write(virtualhost_config)

    run_command("sudo mv /tmp/glpi.conf /etc/apache2/sites-available/glpi.conf")
    run_command("sudo a2ensite glpi.conf")
    run_command("sudo a2enmod rewrite")
    run_command("sudo systemctl reload apache2")

def import_sql_file():
    """Importe la sauvegarde SQL glpi_backup.sql si présente."""
    backup_file = "glpi_backup.sql"
    if not os.path.isfile(backup_file):
        print(f"[INFO] Aucun fichier {backup_file} trouvé, import SQL ignoré.")
        return

    mysql_user = "glpiuser"
    mysql_pwd = getpass.getpass(f"Enter MySQL password for '{mysql_user}' (for SQL import): ")

    command = f"mysql -u {mysql_user} -p{mysql_pwd} glpidb < {backup_file}"

    print("[INFO] Import du fichier SQL dans glpidb...")
    try:
        subprocess.run(command, shell=True, check=True)
        print("[INFO] SQL import successful.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] SQL import failed: {e.stderr}")
        exit(1)

def main():
    try:
        print("[STEP] Fix broken dependencies...")
        fix_broken_dependencies()

        print("[STEP] Install base dependencies (Apache, PHP, MariaDB, etc.)...")
        install_dependencies()

        print("[STEP] Check/install mysql.connector...")
        check_and_install_mysql_connector_python()

        print("[STEP] Configure MariaDB and GLPI database/user...")
        set_mysql_password()

        print("[STEP] Download and deploy GLPI...")
        download_glpi()

        print("[STEP] Configure GLPI PHP config files...")
        configure_glpi()
        configure_config_db_php()

        print("[STEP] Configure Apache VirtualHost for GLPI...")
        configure_virtualhost()

        print("[STEP] Optional: import SQL backup if present...")
        import_sql_file()

        print("[STEP] Remove GLPI install directory (hardening)...")
        run_command("sudo rm -rf /var/www/html/glpi/install")

        print("\n[OK] GLPI installation completed successfully.")
        print("You can now access GLPI at: http://<SERVER_IP>/glpi")
    except Exception as e:
        print(f"[FATAL] Error occurred: {e}")

if __name__ == "__main__":
    main()
