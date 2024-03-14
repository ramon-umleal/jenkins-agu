import subprocess
import os
import re
import requests
import json

def main():
    check_python_apache()
    nomeAplicacao = nomeAplicacao
    jenkins_url = "http://172.17.24.233:8080"
    jenkins_user = "sistema"
    jenkins_token = "11f2680b848a90c255e71a8f1415308bc0"

    # Chamada ao script jenkins.py
    subprocess.run(['python', 'jenkins.py', nomeAplicacao, jenkins_url, jenkins_user, jenkins_token])
    while True:
        print("\nMenu:")
        print("1. Instalar uma nova aplicação com Python e Apache2")
        print("2. Instalar uma nova aplicação com Python e Apache2, em React")
        print("3. Verificar as portas usadas e portas disponíveis")
        print("4. Reiniciar o Apache2")
        print("5. Verificar se já tem aplicação com o nome rodando no servidor")
        print("6. Criar CI/CD no Jenkins")
        print("7. Sair da aplicação")

        choice = input("Escolha uma opção: ")

        if choice == '1':
            nomeAplicacao = input("Digite o nome da aplicação: ")
            if not re.match("^[a-zA-Z][a-zA-Z0-9\-]*$", nomeAplicacao) or len(nomeAplicacao) < 3:
                print("O nome da aplicação deve começar com uma letra, conter apenas letras e números, e ter no mínimo 3 caracteres.")
                continue

            if check_existing_application(nomeAplicacao):
                continue

            server_type = get_server_type()
            portaSistema = create_application_directories(nomeAplicacao, server_type)
            if portaSistema is not None:
                print_report(nomeAplicacao, server_type, portaSistema)
        elif choice == '2':
            pass  # Implementar a instalação com React
        elif choice == '3':
            check_ports()
        elif choice == '4':
            restart_apache()
        elif choice == '5':
            pass  # Implementar a verificação de aplicação pelo nome
        elif choice == '6':
             criar_pipeline_jenkins(nomeAplicacao, jenkins_url, jenkins_user, jenkins_token)     
        elif choice == '7':
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")


def print_report(nomeAplicacao, tipoServidor, portaSistema):
    """
    Imprime um relatório das atividades realizadas durante a execução do programa.
    """
    print("\n--- Relatório de Atividades ---")
    print(f"Nome da Aplicação: {nomeAplicacao}")
    print(f"Tipo de Servidor: {'Homologação' if tipoServidor == '1' else tipoServidor == '2' 'Desenvolvimento'}")
    print(f"Porta Utilizada: {portaSistema}")
    print("Caminhos dos Arquivos Criados/Alterados:")
    print(f"- Diretório da Aplicação: /var/www/{nomeAplicacao}")
    print(f"- Arquivo de Configuração do Apache2: /etc/apache2/sites-available/{nomeAplicacao}.conf")
    print("- Arquivo app.wsgi criado no diretório da aplicação")
    print("- Porta configurada no arquivo /etc/apache2/ports.conf")


def check_python_apache():
    """
    Verifica se Python e Apache estão instalados na máquina.
    Se não estiverem instalados, oferece ao usuário a opção de instalá-los.
    """
    python_version = subprocess.run(['python3', '--version'], capture_output=True, text=True)
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


def check_existing_application(nomeAplicacao):
    """
    Verifica se já existe uma aplicação com o nome fornecido.
    """
    existing_apps = subprocess.run(['ls', '/var/www/'], capture_output=True, text=True)
    existing_apps_list = re.findall(r'\b\w+-' + nomeAplicacao + r'\b', existing_apps.stdout)
    if existing_apps_list:
        print("Já existe uma aplicação com esse nome.")
        print("Aplicações existentes:")
        for app in existing_apps_list:
            print(app)
        return True
    return False


def create_directories(nomeAplicacao):
    """
    Cria os diretórios para a nova aplicação.
    """
    os.makedirs(f"/var/www/{nomeAplicacao}", exist_ok=True)
    os.makedirs(f"/var/www/{nomeAplicacao}/logs", exist_ok=True)
    open(f"/var/www/{nomeAplicacao}/logs/access.log", "w").close()
    open(f"/var/www/{nomeAplicacao}/logs/error.log", "w").close()


def create_venv(nomeAplicacao):
    """
    Cria o ambiente virtual para a aplicação.
    """
    subprocess.run(['python3', '-m', 'venv', f'/var/www/{nomeAplicacao}/venv'])


def create_wsgi_file(nomeAplicacao):
    """
    Cria o arquivo app.wsgi para a aplicação.
    """
    with open(f"/var/www/{nomeAplicacao}/app.wsgi", "w") as wsgi_file:
        wsgi_file.write(f"import sys\n\nsys.path.insert(0, '/var/www/{nomeAplicacao}')\n\nfrom app import app as application")


def configure_ports(portaSistema, ip_servidor, nomeAplicacao):
    """
    Configura a porta no arquivo de configuração do Apache2.
    """
    # Verificar se a porta já está configurada
    with open("/etc/apache2/ports.conf", "r") as ports_conf:
        existing_ports = ports_conf.read()
        if f"Listen {portaSistema}" in existing_ports:
            print(f"A porta {portaSistema} já está configurada.")
            return

    # Verificar se a porta está em uso
    used_ports = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
    if f"LISTEN:{portaSistema}" in used_ports.stdout:
        print(f"A porta {portaSistema} já está em uso.")
        return

    # Se a porta não estiver configurada e não estiver em uso, adicionar ao arquivo
    with open("/etc/apache2/ports.conf", "a") as ports_conf:
        ports_conf.write(f"\nListen {portaSistema}\n")
        dados_adicionais = f"#{ip_servidor}:{portaSistema} - {nomeAplicacao} - /var/www/{nomeAplicacao} - {nomeAplicacao}.conf - venv: /var/www/{nomeAplicacao}/venv\n"
        ports_conf.write(dados_adicionais)
    print(f"Porta {portaSistema} configurada com sucesso.")


def get_server_type():
    """
    Pergunta ao usuário sobre o tipo de servidor (homologação ou desenvolvimento) e retorna o valor.
    """
    while True:
        server_type = input("Selecione o tipo de servidor (1: Homologação, 2: Desenvolvimento): ")
        if server_type in ['1', '2']:
            return "Homologação" if server_type == '1' else "Desenvolvimento"
        else:
            print("Opção inválida. Por favor, escolha 1 para Homologação ou 2 para Desenvolvimento.")


def get_ipv4():
    """
    Obtém o endereço IP IPv4 do servidor.
    """
    try:
        # Obtém o endereço IP IPv4 do servidor usando o comando 'hostname -I'
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        ip_address = result.stdout.strip().split()[0]  # Extrai o primeiro endereço IP da lista
        return ip_address
    except Exception as e:
        print(f"Erro ao obter o endereço IP IPv4 do servidor: {e}")
        return None


def configure_site(nomeAplicacao, ip_servidor, portaSistema):
    """
    Configura o arquivo de configuração do site no Apache2.
    """
    with open(f"/etc/apache2/sites-available/{nomeAplicacao}.conf", "w") as site_conf:
        site_conf.write(f"<VirtualHost *:{portaSistema}>\n")
        site_conf.write(f"\tServerName {ip_servidor}\n")
        site_conf.write(f"\tWSGIDaemonProcess {nomeAplicacao} python-home=/var/www/{nomeAplicacao}/venv user=www-data group=www-data threads=5\n")
        site_conf.write(f"\tWSGIScriptAlias / /var/www/{nomeAplicacao}/app.wsgi\n")
        site_conf.write(f"\t<Directory /var/www/{nomeAplicacao}>\n")
        site_conf.write(f"\t\tWSGIPassAuthorization On\n")
        site_conf.write(f"\t\tWSGIProcessGroup {nomeAplicacao}\n")
        site_conf.write(f"\t\tWSGIApplicationGroup %{{GLOBAL}}\n")
        site_conf.write(f"\t\tOrder deny,allow\n")
        site_conf.write(f"\t\tAllow from all\n")
        site_conf.write(f"\t</Directory>\n")
        site_conf.write(f"\tAlias /static /var/www/{nomeAplicacao}/static\n")
        site_conf.write(f"\t<Directory /var/www/{nomeAplicacao}/static/>\n")
        site_conf.write(f"\t\tOrder allow,deny\n")
        site_conf.write(f"\t\tAllow from all\n")
        site_conf.write(f"\t</Directory>\n")
        site_conf.write(f"\tErrorLog /var/www/{nomeAplicacao}/logs/error.log\n")
        site_conf.write(f"\tCustomLog /var/www/{nomeAplicacao}/logs/access.log combined\n")
        site_conf.write(f"</VirtualHost>\n")

    subprocess.run(['a2ensite', f'{nomeAplicacao}', 'apache2'])
    subprocess.run(['systemctl', 'restart', 'apache2'])
    print("Apache2 reiniciado. e ativando o sistema")

def create_application_directories(nomeAplicacao, server_type):
    """
    Cria os diretórios para a nova aplicação.
    Retorna a porta utilizada.
    """
    # Pergunta ao usuário sobre a porta desejada
    portaSistema_input = input("Digite a porta desejada para a aplicação (ou pressione Enter para porta sequencial a partir de 8200): ")
    if not portaSistema_input:
        portaSistema = find_next_port()
    else:
        portaSistema = int(portaSistema_input)
        if not 8100 <= portaSistema <= 8199:
            print("A porta deve estar entre 8100 e 8199.")
            return None

    create_directories(nomeAplicacao)
    create_venv(nomeAplicacao)
    create_wsgi_file(nomeAplicacao)
    configure_ports(portaSistema, get_ipv4(), nomeAplicacao)

    ip_servidor = get_ipv4()
    if ip_servidor:
        print(f"Endereço IP IPv4 do servidor: {ip_servidor}")

    configure_site(nomeAplicacao, ip_servidor, portaSistema)
    return portaSistema


def find_next_port(start_port=8200):
    """
    Encontra a próxima porta disponível a partir de uma porta inicial.
    """
    used_ports = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
    for port in range(start_port, 8200 + 100):  # Tentar até 8200 + 100 (8300)
        if f"LISTEN:{port}" not in used_ports.stdout:
            return port
    print("Não foi possível encontrar uma porta disponível.")
    return None


def criar_pipeline_jenkins(nomeAplicacao, jenkins_url, jenkins_user, jenkins_token):
    # Definindo o nome do job/pipeline no Jenkins
    github_repo = input("Qual é o endereço da aplicação no GitHub? ")
    descricao_aplicacao = input("Digite a descrição da aplicação (pressione Enter para pular): ")
    # Se a descrição não for fornecida, use o nome da aplicação como descrição
    if not descricao_aplicacao:
        descricao_aplicacao = nomeAplicacao




if __name__ == "__main__":
    main()
