/**
 * Motor de automação no Jenkins 
 * Jenkins Multibranch Pipeline
 * Versão -001.00
 * CONATEC 07/02/2024
 * SISTEMA = "drift"
 */

def sonarQubeAnalysis(String branchName) {
    stage("SonarQube Analysis for ${branchName}") {
        when {
            branch branchName
        }
        environment {
            scannerHome = tool 'SONAR-SCANNER'
        }
        steps {
            node('VM-SDF4673-210') {
                sh "${scannerHome}/bin/sonar-scanner"
            }
        }
    }
}

def devopDeploy() {
    // Carrega o arquivo pipeline-devop.groovy do repositório Git privado
    checkout([$class: 'GitSCM', 
        branches: [[name: 'DEVOP']], 
        userRemoteConfigs: [[
            url: "${GITHUB}",
            credentialsId: 'jenkins-token-git-privado'
        ]]
    ])
    load 'pipeline-devop.groovy'
}

def homologDeploy() {
    echo "load 'pipeline-homolog.groovy"
    // Carrega o arquivo pipeline-homolog.groovy do repositório Git privado
    checkout([$class: 'GitSCM', 
        branches: [[name: 'HOMOLOG']], 
        userRemoteConfigs: [[
            url: "${GITHUB}",
            credentialsId: 'jenkins-token-git-privado'
        ]]
    ])

    load 'pipeline-homolog.groovy'
}
def sendSuccessEmail() {
    emailext (
        to: "${aguEmails}",
        subject: "Multibranch Pipeline server jenkins build:${currentBuild.currentResult} Aplicação: ${SISTEMA}",
        body: "<b>Aplicação: ${SISTEMA}</b><br> Jenkins build: ${env.BUILD_NUMBER}\n\n<br>O build com STATUS:\n${currentBuild.currentResult}\n<br>Job de nome,<b>${env.JOB_NAME}</b>\n<br>Para mais informações\n Acessar o link: ${env.BUILD_URL}<p>\n<br> SonarQube no link: ${SONAQUBE}${SISTEMA}  <br> GITHUB -> ${GITHUB}\n </p> \n <br> link do Sistema ${URLD}\n<br><b>O autor do último commit é: ${GITAUTHOR}</b></br>\n<br> Aplicação ${SISTEMA} <b>está no ar.</b>\n<br> Mensagens de Commit:\n${env.COMMIT_MESSAGES}",
        attachLog: true
    )
}

def sendFailureEmail() {
    script {
        echo "Ixe deu erro da uma olhada nos logs failure"
        // Verifica se os arquivos existem antes de arquivá-los
        sh 'if [ -f /var/www/$SISTEMA/logs/access.log ]; then tail -n 25 /var/www/$SISTEMA/logs/access.log > access.log; fi'
        sh 'if [ -f /var/www/$SISTEMA/logs/error.log ]; then tail -n 25 /var/www/$SISTEMA/logs/error.log > error.log; fi'
    }

    emailext (
        to: "${aguEmails}",
        subject: "Multibranch Pipeline server jenkins build:${currentBuild.currentResult} Aplicação: ${SISTEMA}",
        body: "<b>Aplicação: ${SISTEMA}</b><br> Jenkins build: ${env.BUILD_NUMBER}\n\n<br>O build com STATUS:\n${currentBuild.currentResult}\n<br>Job de nome,<b>${env.JOB_NAME}</b>\n<br>Para mais informações\n Acessar o link: ${env.BUILD_URL}<p>\n<br> SonarQube no link: ${SONAQUBE}${SISTEMA}  <br> GITHUB -> ${GITHUB}\n </p> \n <br> link do Sistema ${URLD}\n<br><b>O autor do último commit é: ${GITAUTHOR}</b></br>\n<br> Aplicação ${SISTEMA} <b>está no ar.</b>",
        attachmentsPattern: '*.log', // Adiciona build.log aos anexos
        attachLog: true
    )
}

pipeline {
    environment {
        aguEmails = "ramon.leal@agu.gov.br,gilson.miranda@agu.gov.br,danilo.nferreira@agu.gov.br,joao.lsouza@agu.gov.br,francisco.dias@agu.gov.br"
        //aguEmails = "ramon.umleal+jenkins@gmail.com"//
        SISTEMA = "drift"//
        APIPATHD = "/home/jenkins/jenkins-agent/workspace/Drift_DEVOP/*"//
        APIPATHH = "/home/jenkins/jenkins-agent/workspace/Drift_HOMOLOG/*"
        PROJ = "/var/www/"
        IPDESENV = "http://sdf4673.agu.gov.br:"
        IPHOMOLOG = "http://sdf4808.agu.gov.br:"
        PORTA = "8081"//
        APPNAME="Sistema Drift"
        GITAUTHOR="${env.GIT_COMMITTER_EMAIL}"
        URLD="${IPDESENV}${PORTA}"
        URLH="${IPHOMOLOG}${PORTA}"
        SONAQUBE ="http://172.17.24.233:9000/dashboard?id="
        GITHUB="https://github.com/agu-pgu/Drift.git"
    }
    agent none // Define o agente como nenhum para o multibranch
    options {
        buildDiscarder logRotator( 
            daysToKeepStr: '16', 
            numToKeepStr: '10'
        )
    }
    stages {
        stage('Build and Test') {
            steps {
                script {
                    // Verifica o nome da branch usando a variável de ambiente BRANCH_NAME
                    if (env.BRANCH_NAME == 'DEVOP') {
                        node('VM-SDF4673-210') {
                            devopDeploy()
                        }
                    } else if (env.BRANCH_NAME == 'HOMOLOG') {
                        node('VM-SDF4808-14') {
                            homologDeploy()
                        }
                    } else {
                        error("Branch não suportada: ${env.BRANCH_NAME}")
                    }
                }
            }
        }
        // Etapa de SonarQube Analysis
        //sonarQubeAnalysis('DEVOP') 
        stage('Capture Commit Messages') {
                steps {
                    script {
                        def changeLogSets = currentBuild.changeSets
                        def commits = []
                        changeLogSets.each { cs ->
                            cs.items.each { item ->
                                commits.add("Commit by ${item.author.fullName}: ${item.msg}")
                            }
                        }
                        env.COMMIT_MESSAGES = commits.join('\n')
                    }
                }
            }
        stage('Email de notificação') {
            steps {
                echo "Email de notificação"
            }
        }
    }
    post {
        success {
            // Etapas a serem executadas quando o pipeline tem sucesso
                sendSuccessEmail()
        }
        failure {
            // Etapas a serem executadas quando o pipeline falha
                sendFailureEmail()
        }
    }
}
