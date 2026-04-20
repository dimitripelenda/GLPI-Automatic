#!/usr/bin/env python3

import subprocess
import getpass

def run(cmd):
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True, check=True)

print("=== Installation GLPI (mode installateur Web) ===")

# 1. Mise à jour système
run("apt update -y")
run("apt upgrade -y")

# 2. Installation Apache, PHP, MariaDB
run("apt install -y apache2 mariadb-server php libapache2-mod-php "
    "php-mysql php-curl php-gd php-xml php-intl php-ldap php-imap php-apcu")

# 3. Activation services
run("systemctl enable apache2")
run("systemctl enable mariadb")
run("systemctl start apache2")
run("systemctl start mariadb")

# 4. Création base GLPI
mysql_pass = getpass.getpass("Mot de passe MySQL pour l'utilisateur GLPI : ")

run("mysql -e \"DROP DATABASE IF EXISTS glpidb;\"")
run("mysql -e \"CREATE DATABASE glpidb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\"")
run("mysql -e \"DROP USER IF EXISTS 'glpiuser'@'localhost';\"")
run(f"mysql -e \"CREATE USER 'glpiuser'@'localhost' IDENTIFIED BY '{mysql_pass}';\"")
run("mysql -e \"GRANT ALL PRIVILEGES ON glpidb.* TO 'glpiuser'@'localhost'; FLUSH PRIVILEGES;\"")

# 5. Téléchargement GLPI
run("cd /tmp && wget https://github.com/glpi-project/glpi/releases/download/10.0.14/glpi-10.0.14.tgz")
run("cd /tmp && tar -xzf glpi-10.0.14.tgz")
run("rm -rf /var/www/html/glpi")
run("mv /tmp/glpi /var/www/html/")

# 6. Permissions
run("chown -R www-data:www-data /var/www/html/glpi")
run("chmod -R 755 /var/www/html/glpi")

# 7. VirtualHost Apache
vhost = """
<VirtualHost *:80>
    ServerAdmin admin@example.com
    DocumentRoot /var/www/html/glpi

    <Directory /var/www/html/glpi>
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
"""

with open("/etc/apache2/sites-available/glpi.conf", "w") as f:
    f.write(vhost)

run("a2ensite glpi.conf")
run("a2enmod rewrite")
run("systemctl reload apache2")

print("\n=== Installation terminée ===")
print("Accédez à l’installateur GLPI : http://<IP>/glpi")
print("L’utilisateur choisira son login et mot de passe.")
