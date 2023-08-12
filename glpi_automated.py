#!/usr/bin/env python3

import os
import re
import subprocess
import getpass

def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Command failed: {result.stderr}")
        exit(1)
    return result.stdout

def install_dependencies():
    packages = [
        'python3-pip', 'mariadb-server', 'apache2', 'php', 'libapache2-mod-php', 'php-imap', 'php-ldap', 'php-curl',
        'php-xmlrpc', 'php-gd', 'php-mysql', 'php-cas', 'php8.1-mysqli', 'php8.1-dom',
        'php8.1-xml', 'php8.1-curl', 'php8.1-gd', 'php8.1-intl', 'apcupsd', 'php-apcu'
    ]
    run_command("sudo apt-get update")
    run_command("sudo apt-get install -y " + " ".join(packages))

def install_mysql_connector_python():
    try:
        subprocess.run(["sudo", "pip3", "install", "mysql-connector-python"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install mysql-connector-python. Error: {e.stderr}")
        exit(1)

def check_and_install_mysql_connector_python():
    try:
        import mysql.connector
    except ImportError:
        install_mysql_connector_python()

def fix_broken_dependencies():
    try:
        run_command("sudo apt --fix-broken install")
    except subprocess.TimeoutExpired:
        print("Package manager is locked. Please wait for it to be available.")
        exit(1)

def install_mariadb():
    run_command("sudo apt-get install -y mariadb-server python3")

def set_mysql_password():
    while True:
        mysql_password = getpass.getpass("Enter a strong password for MySQL (at least 8 characters, with at least one uppercase letter, one lowercase letter, one digit, and one special character): ")
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
            print("Passwords do not match or the password does not meet the complexity criteria. Please try again.")

    run_command(f"sudo mysql -e 'DROP DATABASE IF EXISTS glpidb;'")
    run_command(f"sudo mysql -e 'CREATE DATABASE glpidb;'")
    run_command(f"sudo mysql -e 'GRANT ALL PRIVILEGES ON glpidb.* TO glpiuser@localhost IDENTIFIED BY \"{mysql_password}\";'")
    run_command("sudo mysql -e 'EXIT'")

def download_glpi():
    glpi_url = "https://github.com/glpi-project/glpi/releases/download/10.0.7/glpi-10.0.7.tgz"
    run_command(f"wget {glpi_url}")
    run_command("tar -xvzf glpi-10.0.7.tgz -C /var/www/html")
    run_command("sudo chown -R www-data /var/www/html/glpi/")

def configure_glpi():
    config_file = "/var/www/html/glpi/config/config.php"

    # New database information
    dbhost = 'localhost'
    dbuser = 'glpiuser'
    dbdefault = 'glpidb'
    use_utf8mb4 = True
    allow_myisam = False
    allow_datetime = False
    allow_signed_keys = False

    # Ask the user for the password
    dbpassword = getpass.getpass("Enter the database password for 'glpiuser': ")

    # Create the configuration file content
    config_content = f"""<?php
class DB extends DBmysql {{
   public $dbhost = '{dbhost}';
   public $dbuser = '{dbuser}';
   public $dbpassword = '{dbpassword}';
   public $dbdefault = '{dbdefault}';
   public $use_utf8mb4 = {str(use_utf8mb4).lower()};
   public $allow_myisam = {str(allow_myisam).lower()};
   public $allow_datetime = {str(allow_datetime).lower()};
   public $allow_signed_keys = {str(allow_signed_keys).lower()};
}}
"""

    # Write the new information to the configuration file
    with open(config_file, "w") as f:
        f.write(config_content)

    run_command("sudo systemctl restart apache2")


def configure_config_db_php():
    config_db_file = "/var/www/html/glpi/config/config_db.php"

    # New database information
    dbuser = 'glpiuser'
    dbdefault = 'glpidb'
    dbpassword = getpass.getpass("Enter the database password for 'glpiuser': ")

    # Create the configuration file content
    config_db_content = f"""<?php
class DB extends DBmysql {{
   public $dbhost = 'localhost';
   public $dbuser = '{dbuser}';
   public $dbpassword = '{dbpassword}';
   public $dbdefault = '{dbdefault}';
   public $use_utf8mb4 = true;
   public $allow_myisam = false;
   public $allow_datetime = false;
   public $allow_signed_keys = false;
}}
"""

    # Write the new information to the configuration file
    with open(config_db_file, "w") as f:
        f.write(config_db_content)

# Change the ownership of the config_db.php file to www-data
    run_command(f"sudo chown www-data:www-data {config_db_file}")
    run_command("sudo systemctl restart apache2")


def configure_virtualhost():
    virtualhost_config = """
    <VirtualHost *:80>
        ServerAdmin admin@example.com
        DocumentRoot /var/www/html/glpi/
        ServerName glpi.example.com

        <Directory /var/www/html/glpi/>
            Options FollowSymLinks
            AllowOverride All
            Require all granted
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>
    """
    with open("/etc/apache2/sites-available/glpi.conf", "w") as f:
        f.write(virtualhost_config)
    run_command("sudo a2ensite glpi.conf")
    run_command("sudo systemctl reload apache2")

def import_sql_file():
    mysql_user = "glpiuser"
    mysql_password = getpass.getpass(f"Enter the MySQL password for '{mysql_user}': ")

    command = f"mysql -u {mysql_user} -p{mysql_password} glpidb < glpi_backup.sql"

    try:
        subprocess.run(command, shell=True, check=True)
        print("SQL import successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing SQL import: {e.stderr}")
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

        if os.path.exists("/var/www/html/glpi/config/config.php") and os.path.exists("/var/www/html/glpi/config/config_db.php"):
            print("Installation and configuration of GLPI completed successfully.")
        else:
            print("An error occurred during the installation of GLPI.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
