#!/usr/bin/env python3

import os
import re
import subprocess
import getpass

mysql_password = None

def run_command(command):
    print(f"[RUN] {command}")
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}")
        exit(1)
    return result.stdout

def install_dependencies():
    packages = [
        'mariadb-server', 'apache2', 'php', 'libapache2-mod-php',
        'php-imap', 'php-ldap', 'php-curl', 'php-gd', 'php-mysql',
        'php-xml', 'php-intl', 'php-apcu', 'apcupsd',
        'python3-mysql.connector'
    ]
    run_command("sudo apt update")
    run_command("sudo apt install -y " + " ".join(packages))

def check_mysql_connector():
    try:
        import mysql.connector
        print("[INFO] mysql.connector OK")
    except ImportError:
        print("[INFO] Installing mysql.connector via APT")
        run_command("sudo apt install -y python3-mysql.connector")

def fix_broken_dependencies():
    run_command("sudo apt --fix-broken install -y")

def set_mysql_password():
    global mysql_password

    while True:
        mysql_password = getpass.getpass("Enter MySQL password: ")
        confirm = getpass.getpass("Confirm password: ")

        if mysql_password == confirm:
            break
        print("Passwords do not match.")

    run_command("sudo systemctl enable mariadb")
    run_command("sudo systemctl start mariadb")

    run_command("sudo mysql -e 'DROP DATABASE IF EXISTS glpidb;'")
    run_command("sudo mysql -e 'CREATE DATABASE glpidb CHARACTER SET utf8mb4;'")
    run_command(f"sudo mysql -e \"CREATE USER IF NOT EXISTS 'glpiuser'@'localhost' IDENTIFIED BY '{mysql_password}';\"")
    run_command("sudo mysql -e \"GRANT ALL PRIVILEGES ON glpidb.* TO 'glpiuser'@'localhost'; FLUSH PRIVILEGES;\"")

def download_glpi():
    url = "https://github.com/glpi-project/glpi/releases/download/10.0.7/glpi-10.0.7.tgz"
    run_command("sudo mkdir -p /var/www/html")
    run_command(f"wget -O /tmp/glpi.tgz {url}")
    run_command("sudo tar -xzf /tmp/glpi.tgz -C /var/www/html")
    run_command("sudo chown -R www-data:www-data /var/www/html/glpi")

def configure_glpi():
    config = f"""<?php
class DB extends DBmysql {{
   public $dbhost = 'localhost';
   public $dbuser = 'glpiuser';
   public $dbpassword = '{mysql_password}';
   public $dbdefault = 'glpidb';
}}
"""
    with open("/var/www/html/glpi/config/config_db.php", "w") as f:
        f.write(config)

    run_command("sudo chown www-data:www-data /var/www/html/glpi/config/config_db.php")

def configure_virtualhost():
    server_admin = "admin@example.com"
    server_name = "glpi.local"

    vhost = f"""
<VirtualHost *:80>
    ServerAdmin {server_admin}
    DocumentRoot /var/www/html/glpi/
    ServerName {server_name}

    <Directory /var/www/html/glpi/>
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
"""

    with open("/tmp/glpi.conf", "w") as f:
        f.write(vhost)

    run_command("sudo mv /tmp/glpi.conf /etc/apache2/sites-available/glpi.conf")
    run_command("sudo a2ensite glpi.conf")
    run_command("sudo a2enmod rewrite")
    run_command("sudo systemctl reload apache2")

def main():
    fix_broken_dependencies()
    install_dependencies()
    check_mysql_connector()
    set_mysql_password()
    download_glpi()
    configure_glpi()
    configure_virtualhost()
    run_command("sudo rm -rf /var/www/html/glpi/install")
    print("[OK] GLPI installed. Access: http://<SERVER_IP>/glpi")

if __name__ == "__main__":
    main()
