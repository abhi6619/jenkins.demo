pipeline {

    agent any

    environment {
        DOCKER_IMAGE = 'abhi7677/calculater'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                git(
                    branch: 'main',
                    url: 'https://github.com/abhi6619/jenkins.demo'
                )
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e

                    echo "Building Docker image..."

                    docker build \
                        -t ${DOCKER_IMAGE}:${DOCKER_TAG} .

                    docker tag \
                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        ${DOCKER_IMAGE}:latest

                    echo "Docker build completed."
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

                        echo "Docker login successful."
                    '''
                }
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    set -e

                    echo "Pushing ${DOCKER_IMAGE}:${DOCKER_TAG}"

                    docker push ${DOCKER_IMAGE}:${DOCKER_TAG}

                    echo "Pushing latest tag"

                    docker push ${DOCKER_IMAGE}:latest

                    echo "Docker images pushed successfully."
                '''
            }
        }

        stage('Kubernetes Connection Test') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'jenkins-deployer',
                        variable: 'KUBECONFIG_FILE'
                    )
                ]) {
                    sh '''
                        set -e

                        export KUBECONFIG="$KUBECONFIG_FILE"

                        echo "Testing Kubernetes connection..."

                        kubectl cluster-info

                        echo "Kubernetes identity:"

                        kubectl auth whoami

                        echo "Testing Deployment permission:"

                        kubectl auth can-i create deployments

                        echo "Testing Service permission:"

                        kubectl auth can-i create services

                        echo "Kubernetes connection successful."
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'jenkins-deployer',
                        variable: 'KUBECONFIG_FILE'
                    )
                ]) {
                    sh '''
                        set -e

                        export KUBECONFIG="$KUBECONFIG_FILE"

                        echo "Applying Deployment..."

                        kubectl apply \
                            -f k8s/deployment.yaml

                        echo "Applying Service..."

                        kubectl apply \
                            -f k8s/service.yaml

                        echo "Updating image..."

                        kubectl set image \
                            deployment/calculator \
                            calculator=${DOCKER_IMAGE}:${DOCKER_TAG}

                        echo "Waiting for rollout..."

                        kubectl rollout status \
                            deployment/calculator \
                            --timeout=180s

                        echo "Deployment status:"

                        kubectl get deployment calculator

                        echo "Pod status:"

                        kubectl get pods \
                            -l app=calculator

                        echo "Service status:"

                        kubectl get service calculator
                    '''
                }
            }
        }
    }

    post {

        success {
            echo "========================================"
            echo "PIPELINE SUCCESSFUL"
            echo "========================================"
            echo "Application: Calculator"
            echo "Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
            echo "Kubernetes: Minikube"
            echo "ServiceAccount: jenkins-deployer"
            echo "========================================"
        }

        failure {
            echo "========================================"
            echo "PIPELINE FAILED"
            echo "Check the failed stage in Console Output."
            echo "========================================"
        }

        always {
            echo "Build Number: ${BUILD_NUMBER}"
        }
    }
}
