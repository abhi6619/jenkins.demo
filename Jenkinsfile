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
                    set -e

                    echo "Building Docker image..."
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .

                    echo "Creating latest tag..."
                    docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest

                    echo "Images created:"
                    docker images | grep calculater
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

                        echo "Logging in to Docker Hub..."

                        printf '%s' "$DOCKER_PASSWORD" | \
                        docker login docker.io \
                        --username "$DOCKER_USER" \
                        --password-stdin

                        echo "Docker Hub login successful."
                    '''
                }
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    set -e

                    echo "Pushing versioned image..."
                    docker push ${DOCKER_IMAGE}:${DOCKER_TAG}

                    echo "Pushing latest image..."
                    docker push ${DOCKER_IMAGE}:latest

                    echo "Docker images pushed successfully."
                '''
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
                        set -e

                        echo "Checking Kubernetes connection..."
                        kubectl cluster-info

                        echo "Deploying Kubernetes manifests..."
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml

                        echo "Updating deployment image..."
                        kubectl set image deployment/calculator \
                            calculator=${DOCKER_IMAGE}:${DOCKER_TAG}

                        echo "Waiting for rollout..."
                        kubectl rollout status deployment/calculator \
                            --timeout=180s

                        echo "Deployment status:"
                        kubectl get deployment calculator

                        echo "Pods:"
                        kubectl get pods -l app=calculator

                        echo "Service:"
                        kubectl get service calculator
                    '''
                }
            }
        }
    }

    post {

        success {
            echo """
            ========================================
            PIPELINE SUCCESSFUL
            ========================================
            Docker Image : ${DOCKER_IMAGE}:${DOCKER_TAG}
            Kubernetes   : Minikube
            Deployment   : calculator
            ========================================
            """
        }

        failure {
            echo """
            ========================================
            PIPELINE FAILED
            ========================================
            Check the failed stage in the console.
            ========================================
            """
        }

        always {
            echo "Build Number: ${BUILD_NUMBER}"
        }
    }
}
