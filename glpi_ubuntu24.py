#!/usr/bin/env python3

import subprocess
import getpass

mysql_password = None


def run_command(command):
    """Exécute une commande shell et arrête le script en cas d'erreur."""
    print(f"[RUN] {command}")
    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        print("Command failed")
        exit(1)


def fix_broken_dependencies():
    """Répare les dépendances cassées."""
    run_command("apt --fix-broken install -y")


def install_dependencies():
    """Installe les dépendances nécessaires pour GLPI."""

    packages = [
        "apache2",
        "mariadb-server",
        "php",
        "libapache2-mod-php",
        "php-imap",
        "php-ldap",
        "php-curl",
        "php-gd",
        "php-mysql",
        "php-xml",
        "php-intl",
        "php-apcu",
        "php-mbstring",
        "php-zip",
        "php-bz2",
        "wget",
        "tar"
    ]

    run_command("apt update")
    run_command("apt upgrade -y")

    pkg_string = " ".join(packages)

    run_command(f"apt install -y {pkg_string}")


def configure_mariadb():
    """Configure MariaDB et crée la base GLPI."""

    global mysql_password

    print("\n[INFO] Configuration MariaDB")

    while True:
        mysql_password = getpass.getpass("Enter password for GLPI database user: ")
        confirm_password = getpass.getpass("Confirm password: ")

        if mysql_password == confirm_password and len(mysql_password) >= 8:
            break
        else:
            print("Passwords do not match or too short.")

    run_command("systemctl enable mariadb")
    run_command("systemctl start mariadb")

    run_command(
        "mysql -e \"CREATE DATABASE IF NOT EXISTS glpidb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\""
    )

    run_command(
        f"mysql -e \"CREATE USER IF NOT EXISTS 'glpiuser'@'localhost' IDENTIFIED BY '{mysql_password}';\""
    )

    run_command(
        "mysql -e \"GRANT ALL PRIVILEGES ON glpidb.* TO 'glpiuser'@'localhost';\""
    )

    run_command("mysql -e \"FLUSH PRIVILEGES;\"")


def download_glpi():
    """Télécharge et installe GLPI."""

    print("\n[INFO] Downloading GLPI")

    run_command(
        "wget -O /tmp/glpi.tgz https://github.com/glpi-project/glpi/releases/latest/download/glpi.tgz"
    )

    run_command("mkdir -p /var/www")

    run_command("tar -xzf /tmp/glpi.tgz -C /var/www")

    run_command("chown -R www-data:www-data /var/www/glpi")

    run_command("chmod -R 775 /var/www/glpi/files")
    run_command("chmod -R 775 /var/www/glpi/config")
    run_command("chmod -R 775 /var/www/glpi/marketplace")
    run_command("chmod -R 775 /var/www/glpi/plugins")


def configure_apache():
    """Configure le VirtualHost Apache."""

    print("\n[INFO] Configure Apache")

    server_admin = input("ServerAdmin email: ").strip() or "admin@example.com"
    server_name = input("ServerName (ex: glpi.local): ").strip() or "glpi.local"

    vhost = f"""
<VirtualHost *:80>

ServerAdmin {server_admin}
ServerName {server_name}

DocumentRoot /var/www/glpi/public

<Directory /var/www/glpi/public>

Require all granted
AllowOverride All

</Directory>

ErrorLog ${{APACHE_LOG_DIR}}/glpi_error.log
CustomLog ${{APACHE_LOG_DIR}}/glpi_access.log combined

</VirtualHost>
"""

    with open("/tmp/glpi.conf", "w") as f:
        f.write(vhost)

    run_command("mv /tmp/glpi.conf /etc/apache2/sites-available/glpi.conf")

    run_command("a2ensite glpi.conf")

    run_command("a2enmod rewrite")

    run_command("systemctl restart apache2")


def finish():

    print("\n=====================================")
    print("GLPI installation completed")
    print("=====================================")

    print("\nOpen your browser:")
    print("http://SERVER-IP")

    print("\nDatabase configuration:")
    print("Database: glpidb")
    print("User: glpiuser")
    print("Host: localhost")


def main():

    fix_broken_dependencies()

    install_dependencies()

    configure_mariadb()

    download_glpi()

    configure_apache()

    finish()


if __name__ == "__main__":
    main()
