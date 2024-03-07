import requests
import xml.etree.ElementTree as ET


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
    pipeline_name = f"{nomeAplicacao}-pipeline"
    pipeline_config_xml = f"""
        <flow-definition plugin="workflow-job@2.40">
            <actions/>
            <description></description>
            <keepDependencies>false</keepDependencies>
            <properties/>
            <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.89">
                <scm class="hudson.plugins.git.GitSCM" plugin="git@4.11.0">
                    <configVersion>2</configVersion>
                    <userRemoteConfigs>
                        <hudson.plugins.git.UserRemoteConfig>
                            <url>GIT_URL</url> <!-- Substitua GIT_URL pela URL do seu repositório Git -->
                        </hudson.plugins.git.UserRemoteConfig>
                    </userRemoteConfigs>
                    <branches>
                        <hudson.plugins.git.BranchSpec>
                            <name>*/master</name>
                        </hudson.plugins.git.BranchSpec>
                    </branches>
                    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                    <submoduleCfg class="list"/>
                    <extensions/>
                </scm>
                <scriptPath>Jenkinsfile</scriptPath>
            </definition>
            <triggers/>
            <disabled>false</disabled>
        </flow-definition>
    """
    try:
        response = session.post(
            f"{jenkins_url}/createItem?name={pipeline_name}",
            headers={"Content-Type": "application/xml"},
            data=pipeline_config_xml
        )
        response.raise_for_status()
        print(f"Pipeline '{pipeline_name}' criado com sucesso!")
    except Exception as e:
        print(f"Falha ao criar o pipeline '{pipeline_name}' no Jenkins: {e}")
# Exemplo de uso
def main():
    nomeAplicacao = "3-minha-aplicacao"
    jenkins_url = "http://172.17.24.233:8080"
    jenkins_user = "sistema"
    jenkins_token = "11f2680b848a90c255e71a8f1415308bc0"

    session = conectar_jenkins(jenkins_url, jenkins_user, jenkins_token)
    if session:
        criar_pipeline(session, nomeAplicacao, jenkins_url)

if __name__ == "__main__":
    main()
                    