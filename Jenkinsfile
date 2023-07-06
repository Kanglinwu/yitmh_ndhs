/* groovylint-disable-next-line CompileStatic */
pipeline {
    agent {
        label 'vm_10.7.6.223'
    }
    stages {
        stage('doing the quasar build') {
            steps {
                echo 'Under building'
                sh 'cd /home/ops/handover/frontend/code && quasar build'
            }
        }
        stage('restart docker') {
            steps {
                echo 'restarting docker container - nginx_quasar'
                sh 'docker restart nginx_quasar'
            }
        }
    }
}
