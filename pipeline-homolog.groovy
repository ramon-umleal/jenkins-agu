/**
 * Motor de automação no Jenkins 
 * Jenkins Multibranch Pipeline
 * Versão -001.00
 * CONATEC 07/02/2024
 * SISTEMA = "drift"
 */
def buildStep(String url) {
    stage('Build') {
            script {
                def response = httpRequest(url)//URLH
                println("Status: " + response.status)
                if (response.status.toString() != "200") {
                    println "ERROR: " + errorMsg
                } else {
                    println "ALL OK!!!. Job ${env.JOB_NAME} Pagina WEB OK deu status ${response.status} agora sim!!!"
                    sh 'touch SUCCESS.log'
                }
            }
    }
}
def checkVersions() {
    echo '---Verificando Versões----'
    sh 'python3 --version'
    sh 'hostname'
    sh 'ifconfig eth0 | grep inet'
}
def getGitAuthor() {
    return sh(script: 'git log -1 --format=%an', returnStdout: true).trim()
}
    stage('Deploy Code to Development') {   
        echo "Deploy to Dev"
            checkVersions()
                script {
                    GITAUTHOR = getGitAuthor()
                    echo "O autor do último commit é: ${GITAUTHOR}"                
                }
        }
    stage('Develop Branch Deploy Code') {
        echo "Deploying Code from Develop branch"
        checkVersions()   
    }
    stage('Copiando os arquivos'){
            echo '----------Copiando os arquivos--------------------' 
            sh 'cp -R $APIPATHH $PROJ$SISTEMA/' 
        }
    stage('reload apache'){  
            echo '-----------reload APACHE2-----------------'
            sh '/etc/init.d/apache2 restart'
        }
    stage('Build and Test') {
            script {
                    // Chama a função buildStep passando a URL desejada
                buildStep("http://sdf4808.agu.gov.br:8081")//              
            } 
    }
