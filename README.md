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
def install_dependencies():
    packages = [
        'python3-pip', 'mariadb-server', 'apache2', 'php', 'libapache2-mod-php', 'php-imap', 'php-ldap', 'php-curl',
        'php-xmlrpc', 'php-gd', 'php-mysql', 'php-cas', 'php8.1-mysqli', 'php8.1-dom',
        'php8.1-xml', 'php8.1-curl', 'php8.1-gd', 'php8.1-intl', 'apcupsd', 'php-apcu'
    ]
    run_command("sudo apt-get update")
    run_command("sudo apt-get install -y " + " ".join(packages))

# 2. Installation de connecteur MySQL pour Python.
def install_mysql_connector_python():
    try:
        subprocess.run(["sudo", "pip3", "install", "mysql-connector-python"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install mysql-connector-python. Error: {e.stderr}")
        exit(1)

# 3. Vérification et installation de connecteur MySQL pour Python si nécessaire.
def check_and_install_mysql_connector_python():
    try:
        import mysql.connector
    except ImportError:
        install_mysql_connector_python()

# 4. Répare les dépendances cassées du système.
def fix_broken_dependencies():
    try:
        run_command("sudo apt --fix-broken install")
    except subprocess.TimeoutExpired:
        print("Package manager is locked. Please wait for it to be available.")
        exit(1)

# 5. Installation MariaDB et Python3.
def install_mariadb():
    run_command("sudo apt-get install -y mariadb-server python3")
    
# 6. Configuration de mot de passe MySQL pour l'utilisateur 'glpiuser'
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
    
# 7. Téléchargement et extraction GLPI depuis une URL spécifique
def download_glpi():
    glpi_url = "https://github.com/glpi-project/glpi/releases/download/10.0.7/glpi-10.0.7.tgz"
    run_command(f"wget {glpi_url}")
    run_command("tar -xvzf glpi-10.0.7.tgz -C /var/www/html")
    run_command("sudo chown -R www-data /var/www/html/glpi/")

# 8. Configure le fichier de configuration de GLPI
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

# 9. Configuration de fichier config_db.php pour la base de données.
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

# 10. Configuration de virtualhost Apache pour GLPI
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

# 11. Importation du fichier SQL dans la base de données
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
# 12. Fonction principale pour l'installation et la configuration de GLPI
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

# Exécution du script Python
Création de fichier Python
touch glpi_automated.py

Exécuter un script Python
Après avoir copié le script, rendez le script exécutable à l'aide de la commande suivante :

chmod +x glpi_automated.py

exécutez ce script comme ci-dessous : 
Notez bien le script doit etre dans le meme repertoire que le fichier sql: glpi_backup.sql
./glpi_automated.py
