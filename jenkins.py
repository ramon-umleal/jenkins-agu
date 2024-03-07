import requests

nomeAplicacao="teste"

def conectar_jenkins(jenkins_url, jenkins_user, jenkins_token):

    try:
        session = requests.Session()
        session.auth = (jenkins_user, jenkins_token)
        session.headers.update({'Content-Type': 'application/json'})
        # Testa a conexão obtendo informações do Jenkins
        response = session.get(f"{jenkins_url}/api/json")
        response.raise_for_status()  # Lança uma exceção se a resposta não for bem-sucedida
        print("Conexão com Jenkins estabelecida com sucesso.")
        return session
    except Exception as e:
        print(f"Erro ao conectar-se ao Jenkins: {e}")
        return None

def criar_pipeline(session, nomeAplicacao, jenkins_url):
    """
    Cria um pipeline no Jenkins com o nome fornecido.
    """
    pipeline_name = f"{nomeAplicacao}-pipeline"
    pipeline_config = {
        "name": pipeline_name,
        "mode": "org.jenkinsci.plugins.workflow.job.WorkflowJob",
        "from": "",
        "Jenkinsfile": "Jenkinsfile"
    }
    try:
        response = session.post(
            f"{jenkins_url}/createItem",
            json=pipeline_config
        )
        response.raise_for_status()  # Lança uma exceção se a resposta não for bem-sucedida  
        print(f"Pipeline '{pipeline_name}' criado com sucesso!")
    except Exception as e:
        print(f"Falha ao criar o pipeline '{pipeline_name}' no Jenkins: {e}")

# Exemplo de uso
def main():
    nomeAplicacao = "minha-aplicacao"
    jenkins_url = "http://172.17.24.233:8080"
    jenkins_user = "sistema"
    jenkins_token = "11f2680b848a90c255e71a8f1415308bc0"

    session = conectar_jenkins(jenkins_url, jenkins_user, jenkins_token)
    if session:
        criar_pipeline(session, nomeAplicacao, jenkins_url)

if __name__ == "__main__":
    main()
                    