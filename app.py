import subprocess
import os
import re

# Variável global para armazenar o link do repositório Git
git_repo_link = "https://github.com/ramon-umleal/jenkins-agu.git"

def check_python_apache():
    """
    Verifica se Python e Apache estão instalados na máquina.
    Se não estiverem instalados, oferece ao usuário a opção de instalá-los.
    """
    python_version = subprocess.run(['python', '--version'], capture_output=True, text=True)
    apache_version = subprocess.run(['apache2', '-v'], capture_output=True, text=True)
    
    if python_version.returncode != 0 or apache_version.returncode != 0:
        print("Python ou Apache não estão instalados.")
        install_python_apache()

def install_python_apache():
    """
    Instala Python e Apache2 via apt-get se não estiverem instalados.
    """
    install_python = input("Python não está instalado. Deseja instalar? (y/n): ")
    if install_python.lower() == 'y':
        subprocess.run(['apt-get', 'install', 'python3.10', 'python3.10-venv', '-y'])

    install_apache = input("Apache2 não está instalado. Deseja instalar? (y/n): ")
    if install_apache.lower() == 'y':
        # Instalação do Apache2
        apache_install_commands = [
            "apt-get install apache2 -y",
            "/etc/init.d/apache2 start",
            "a2enmod wsgi",
            "a2enmod headers",
            "a2enmod rewrite",
            "systemctl restart apache2"
        ]

        for command in apache_install_commands:
            print(f"Executando: {command}")
            subprocess.run(command, shell=True)

def check_ports():
    """
    Verifica as portas usadas e disponíveis.
    """
    used_ports = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
    print("Portas em uso:")
    print(used_ports.stdout)

def restart_apache():
    """
    Reinicia o Apache2.
    """
    subprocess.run(['systemctl', 'restart', 'apache2'])
    print("Apache2 reiniciado.")

def check_existing_application(name):
    """
    Verifica se já existe uma aplicação com o nome fornecido.
    """
    existing_apps = subprocess.run(['ls', '/var/www/'], capture_output=True, text=True)
    existing_apps_list = re.findall(r'\b\w+-' + name + r'\b', existing_apps.stdout)
    if existing_apps_list:
        print("Já existe uma aplicação com esse nome.")
        print("Aplicações existentes:")
        for app in existing_apps_list:
            print(app)
        return True
    return False

def create_application_directories(name, server_type):
    """
    Cria os diretórios para a nova aplicação.
    """
    # Pergunta ao usuário sobre o nome e tipo do servidor
    tipoServidor = server_type

    # Pergunta ao usuário sobre a porta desejada
    portaSistema = input("Digite a porta desejada para a aplicação (ou pressione Enter para porta sequencial a partir de 8200): ")
    if not portaSistema:
        portaSistema = 8200
    elif not 8100 <= int(portaSistema) <= 8199:
        print("A porta deve estar entre 8100 e 8199.")
        return

    # Criação dos diretórios
    os.makedirs(f"/var/www/{name}", exist_ok=True)
    os.makedirs(f"/var/www/{name}/logs", exist_ok=True)

    # Criação do ambiente virtual
    subprocess.run(['python3', '-m', 'venv', f'/var/www/{name}/venv'])

    # Criação do arquivo app.wsgi
    with open(f"/var/www/{name}/app.wsgi", "w") as wsgi_file:
        wsgi_file.write(f"import sys\n\nsys.path.insert(0, '/var/www/{name}')\n\nfrom app import app as application")

    # Configuração da porta no Apache2
    with open("/etc/apache2/ports.conf", "a") as ports_conf:
        ports_conf.write(f"\nListen {portaSistema}\n")

    # Configuração do arquivo de configuração do site
    with open(f"/etc/apache2/sites-available/{name}.conf", "w") as site_conf:
        site_conf.write(f"<VirtualHost *:{portaSistema}>\n")
        site_conf.write(f"\tServerName {tipoServidor}\n")
        site_conf.write(f"\tWSGIDaemonProcess {name} python-home=/var/www/{name}/venv user=www-data group=www-data threads=5\n")
        site_conf.write(f"\tWSGIScriptAlias / /var/www/{name}/app.wsgi\n")
        site_conf.write(f"\t<Directory /var/www/{name}>\n")
        site_conf.write(f"\t\tWSGIPassAuthorization On\n")
        site_conf.write(f"\t\tWSGIProcessGroup {name}\n")
        site_conf.write(f"\t\tWSGIApplicationGroup %{GLOBAL}\n")
        site_conf.write(f"\t\tOrder deny,allow\n")
        site_conf.write(f"\t\tAllow from all\n")
        site_conf.write(f"\t</Directory>\n")
        site_conf.write(f"\tAlias /static /var/www/{name}/static\n")
        site_conf.write(f"\t<Directory /var/www/{name}/static/>\n")
        site_conf.write(f"\t\tOrder allow,deny\n")
        site_conf.write(f"\t\tAllow from all\n")
        site_conf.write(f"\t</Directory>\n")
        site_conf.write(f"\tErrorLog /var/www/{name}/logs/error.log\n")
        site_conf.write(f"\tCustomLog /var/www/{name}/logs/access.log combined\n")
        site_conf.write(f"</VirtualHost>\n")

def main():
    check_python_apache()

    while True:
        print("\nMenu:")
        print("1. Instalar uma nova aplicação com Python e Apache2")
        print("2. Instalar uma nova aplicação com Python e Apache2, em React")
        print("3. Verificar as portas usadas e portas disponíveis")
        print("4. Reiniciar o Apache2")
        print("5. Verificar se já tem aplicação com o nome rodando no servidor")
        print("6. Sair da aplicação")

        choice = input("Escolha uma opção: ")

        if choice == '1':
            name = input("Digite o nome da aplicação: ")
            if not re.match("^[a-zA-Z][a-zA-Z0-9]*$", name) or len(name) < 3:
                print("O nome da aplicação deve começar com uma letra, conter apenas letras e números, e ter no mínimo 3 caracteres.")
                continue

            if check_existing_application(name):
                continue

            server_type = input("Selecione o tipo de servidor (1: Homologação, 2: Desenvolvimento): ")
            create_application_directories(name, server_type)
        elif choice == '2':
            pass  # Implementar a instalação com React
        elif choice == '3':
            check_ports()
        elif choice == '4':
            restart_apache()
        elif choice == '5':
            pass  # Implementar a verificação de aplicação pelo nome
        elif choice == '6':
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()
