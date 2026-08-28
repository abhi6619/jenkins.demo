pipeline {

    agent any

    environment {
        DOCKER_IMAGE = "abhi7677/calculater"
        DOCKER_TAG   = "${BUILD_NUMBER}"
        KUBE_SERVER  = "https://kubernetes.default.svc"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'http://github.com/abhi6619/jenkins.demo'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Docker Login') {
    steps {
        withCredentials([
            usernamePassword(
                credentialsId: 'dockerhub-credentials',
                usernameVariable: 'DOCKER_USER',
                passwordVariable: 'DOCKER_PASSWORD'
            )
        ]) {
            sh '''
                set -e

                printf '%s' "$DOCKER_PASSWORD" | docker login docker.io \
                    --username "$DOCKER_USER" \
                    --password-stdin
            '''
        }
    }
}
        stage('Deploy to Minikube') {
            steps {
                withKubeConfig([
                    credentialsId: 'jenkins-deployer',
                    serverUrl: "${KUBE_SERVER}",
                    namespace: 'default'
                ]) {
                    sh '''
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml

                        kubectl set image deployment/calculator \
                          calculator=${DOCKER_IMAGE}:${DOCKER_TAG}

                        kubectl rollout status deployment/calculator
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Application deployed successfully!"
            echo "Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
        }

        failure {
            echo "Pipeline failed. Check Jenkins console output."
        }
    }
}
