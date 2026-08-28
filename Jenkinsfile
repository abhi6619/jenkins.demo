pipeline {

    agent any

    environment {
        DOCKER_IMAGE = 'abhi7677/calculater'
        DOCKER_TAG   = "${BUILD_NUMBER}"

        MINIKUBE_HOST = '192.168.14.62'
        LOCAL_API_PORT = '8443'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'

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

                    echo "Docker build successful."

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

        stage('Push Docker Image') {
            steps {
                sh '''
                    set -e

                    echo "Pushing image: ${DOCKER_IMAGE}:${DOCKER_TAG}"

                    docker push ${DOCKER_IMAGE}:${DOCKER_TAG}

                    echo "Pushing latest image..."

                    docker push ${DOCKER_IMAGE}:latest

                    echo "Docker images pushed successfully."
                '''
            }
        }

        stage('Create SSH Tunnel') {
            steps {

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'minikube-ssh',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "Creating SSH tunnel..."

                        chmod 600 "$SSH_KEY"

                        # Remove an existing tunnel
                        pkill -f "ssh.*8443:127.0.0.1:32771" || true

                        # Create SSH tunnel
                        ssh -f -N \
                            -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            -o ExitOnForwardFailure=yes \
                            -L 8443:127.0.0.1:32771 \
                            ${SSH_USER}@${MINIKUBE_HOST}

                        echo "SSH tunnel created successfully."

                        sleep 2

                        echo "Testing Kubernetes API..."

                        curl -k -m 10 \
                            https://127.0.0.1:8443/version

                        echo ""
                        echo "Kubernetes API is reachable."
                    '''
                }
            }
        }

        stage('Kubernetes Authentication') {
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

                        echo "----------------------------------------"
                        echo "Kubernetes Identity"
                        echo "----------------------------------------"

                        kubectl auth whoami

                        echo "----------------------------------------"
                        echo "RBAC Validation"
                        echo "----------------------------------------"

                        echo "Create Deployment:"
                        kubectl auth can-i create deployments

                        echo "Update Deployment:"
                        kubectl auth can-i update deployments

                        echo "Create Service:"
                        kubectl auth can-i create services

                        echo "Get Pods:"
                        kubectl auth can-i get pods

                        echo "Kubernetes authentication successful."
                    '''
                }
            }
        }

        stage('Deploy Application') {
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

                        echo "Deploying Kubernetes resources..."

                        kubectl apply \
                            -f k8s/deployment.yaml

                        kubectl apply \
                            -f k8s/service.yaml

                        echo "Updating deployment image..."

                        kubectl set image \
                            deployment/calculator \
                            calculator=${DOCKER_IMAGE}:${DOCKER_TAG}

                        echo "Waiting for rollout..."

                        kubectl rollout status \
                            deployment/calculator \
                            --timeout=180s

                        echo "----------------------------------------"
                        echo "Deployment"
                        echo "----------------------------------------"

                        kubectl get deployment calculator

                        echo "----------------------------------------"
                        echo "Pods"
                        echo "----------------------------------------"

                        kubectl get pods \
                            -l app=calculator \
                            -o wide

                        echo "----------------------------------------"
                        echo "Service"
                        echo "----------------------------------------"

                        kubectl get service calculator
                    '''
                }
            }
        }
    }

    post {

        success {
            echo """
============================================
       PIPELINE SUCCESSFUL
============================================

Application:
Calculator

Docker Image:
${DOCKER_IMAGE}:${DOCKER_TAG}

Minikube VM:
${MINIKUBE_HOST}

Kubernetes ServiceAccount:
jenkins-deployer

============================================
"""
        }

        failure {
            echo """
============================================
          PIPELINE FAILED
============================================

Check the failed stage in the Jenkins
console output.

============================================
"""
        }

        always {
            sh '''
                echo "Cleaning SSH tunnel..."

                pkill -f "ssh.*8443:127.0.0.1:32771" || true
            '''

            echo "Build Number: ${BUILD_NUMBER}"
        }
    }
}
