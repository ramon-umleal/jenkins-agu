import requests
import xml.etree.ElementTree as ET
import sys



def conectar_jenkins(jenkins_url, jenkins_user, jenkins_token):

    try:
        session = requests.Session()
        session.auth = (jenkins_user, jenkins_token)
        session.headers.update({"Content-Type": "application/json"})
        # Testa a conexão obtendo informações do Jenkins
        response = session.get(f"{jenkins_url}/api/json")
        response.raise_for_status()  # Lança uma exceção se a resposta não for bem-sucedida
        print("Conexão com Jenkins estabelecida com sucesso.")
        return session
    except Exception as e:
        print(f"Erro ao conectar-se ao Jenkins: {e}")
        return None


def criar_pipeline(session, nomeAplicacao, github_repo, descricao_aplicacao, jenkins_url, tipo_branch):
    pipeline_name = f"{nomeAplicacao}-pipeline"
    pipeline_config_xml = f"""
     <flow-definition plugin="workflow-job@1385.vb_58b_86ea_fff1">
    <actions/>
    <description>Teste de criação job no Jenkins {nomeAplicacao}</description>
    <keepDependencies>false</keepDependencies>
    <properties>
        <org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
            <triggers>
                <hudson.triggers.SCMTrigger>
                    <spec>H/20 * * * *</spec>
                    <ignorePostCommitHooks>false</ignorePostCommitHooks>
                </hudson.triggers.SCMTrigger>
            </triggers>
        </org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
    </properties>
    <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@3880.vb_ef4b_5cfd270">
        <scm class="hudson.plugins.git.GitSCM" plugin="git@5.2.1">
            <configVersion>2</configVersion>
            <userRemoteConfigs>
                <hudson.plugins.git.UserRemoteConfig>
                    <url>{github_repo}</url>
                    <credentialsId>jenkins-token-git-privado</credentialsId>
                </hudson.plugins.git.UserRemoteConfig>
            </userRemoteConfigs>
            <branches>
                <hudson.plugins.git.BranchSpec>
                    <name>*/DEVOP</name>
                </hudson.plugins.git.BranchSpec>
            </branches>
            <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
            <gitTool>default</gitTool>
            <submoduleCfg class="empty-list"/>
            <extensions/>
        </scm>
        <scriptPath>Jenkinsfile</scriptPath>
        <lightweight>false</lightweight>
    </definition>
    <triggers/>
    <disabled>false</disabled>
</flow-definition>
    """
    try:
        response = session.post(
            f"{jenkins_url}/createItem?name={pipeline_name}",
            headers={"Content-Type": "application/xml"},
            data=pipeline_config_xml,
        )
        if response.status_code == 200:
            print(f"Pipeline '{pipeline_name}' criado com sucesso!")
        elif response.status_code == 400:
            print(
                f"Já existe um pipeline com o nome '{pipeline_name}' no Jenkins porfavor escolher  outro nome."
            )
        else:
            response.raise_for_status()
    except Exception as e:
        print(f"Falha ao criar o pipeline '{pipeline_name}' no Jenkins: {e}")



def main():
    nomeAplicacao = sys.argv[1]
    jenkins_url = sys.argv[2]
    jenkins_user = sys.argv[3]
    jenkins_token = sys.argv[4]
    github_repo = sys.argv[5]
    descricao_aplicacao = sys.argv[6]
    tipo_branch = sys.argv[7]

    session = conectar_jenkins(jenkins_url, jenkins_user, jenkins_token)
    if session:
        criar_pipeline(session, nomeAplicacao, github_repo, descricao_aplicacao, jenkins_url, tipo_branch)


if __name__ == "__main__":
    main()
