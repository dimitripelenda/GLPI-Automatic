#!/usr/bin/env python3

import subprocess
import getpass

def run(cmd):
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def install_packages():

    packages = [
        "apache2",
        "mariadb-server",
        "php",
        "libapache2-mod-php",
        "php-mysql",
        "php-curl",
        "php-gd",
        "php-intl",
        "php-xml",
        "php-mbstring",
        "php-bz2",
        "php-zip",
        "php-imap",
        "php-ldap",
        "php-apcu",
        "wget",
        "tar"
    ]

    run("apt update")
    run("apt upgrade -y")

    pkg_string = " ".join(packages)

    run(f"apt install -y {pkg_string}")

def configure_mariadb():

    print("\n[INFO] Configure MariaDB for GLPI")

    db_password = getpass.getpass("Enter password for GLPI database user: ")

    run("systemctl enable mariadb")
    run("systemctl start mariadb")

    run("mysql -e \"CREATE DATABASE IF NOT EXISTS glpidb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\"")

    run(f"mysql -e \"CREATE USER IF NOT EXISTS 'glpiuser'@'localhost' IDENTIFIED BY '{db_password}';\"")

    run("mysql -e \"GRANT ALL PRIVILEGES ON glpidb.* TO 'glpiuser'@'localhost';\"")

    run("mysql -e \"FLUSH PRIVILEGES;\"")

def install_glpi():

    print("\n[INFO] Downloading GLPI")

    run("wget -O /tmp/glpi.tgz https://github.com/glpi-project/glpi/releases/latest/download/glpi.tgz")

    run("mkdir -p /var/www")

    run("tar -xzf /tmp/glpi.tgz -C /var/www")

    run("chown -R www-data:www-data /var/www/glpi")

    run("chmod -R 775 /var/www/glpi/files")
    run("chmod -R 775 /var/www/glpi/config")
    run("chmod -R 775 /var/www/glpi/marketplace")
    run("chmod -R 775 /var/www/glpi/plugins")

def configure_apache():

    print("\n[INFO] Configure Apache VirtualHost")

    servername = input("ServerName (ex: glpi.local): ").strip() or "glpi.local"

    vhost = f"""
<VirtualHost *:80>

ServerName {servername}

DocumentRoot /var/www/glpi/public

<Directory /var/www/glpi/public>

Require all granted
AllowOverride All

</Directory>

ErrorLog ${{APACHE_LOG_DIR}}/glpi_error.log
CustomLog ${{APACHE_LOG_DIR}}/glpi_access.log combined

</VirtualHost>
"""

    with open("/etc/apache2/sites-available/glpi.conf", "w") as f:
        f.write(vhost)

    run("a2ensite glpi.conf")

    run("a2enmod rewrite")

    run("systemctl reload apache2")

def finish():

    print("\n[OK] GLPI installation finished\n")

    print("Open your browser:")
    print("http://SERVER-IP")

    print("\nThen finish installation via the web installer.")

def main():

    install_packages()

    configure_mariadb()

    install_glpi()

    configure_apache()

    finish()

if __name__ == "__main__":
    main()
