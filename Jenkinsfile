pipeline {

    agent any

    environment {
        DOCKER_IMAGE = 'abhi7677/calculater'
        DOCKER_TAG   = "${BUILD_NUMBER}"

        MINIKUBE_VM  = '192.168.14.62'
        LOCAL_API    = '127.0.0.1:8443'
        REMOTE_API   = '127.0.0.1:32771'
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

                    echo "========================================"
                    echo "BUILDING DOCKER IMAGE"
                    echo "========================================"

                    docker build \
                        -t ${DOCKER_IMAGE}:${DOCKER_TAG} .

                    docker tag \
                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        ${DOCKER_IMAGE}:latest

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

                        echo "========================================"
                        echo "DOCKER HUB LOGIN"
                        echo "========================================"

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

                    echo "========================================"
                    echo "PUSHING IMAGE"
                    echo "========================================"

                    docker push ${DOCKER_IMAGE}:${DOCKER_TAG}

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

                        echo "========================================"
                        echo "CREATING SSH TUNNEL"
                        echo "========================================"

                        chmod 600 "$SSH_KEY"

                        # Remove an old tunnel if present
                        pkill -f "127.0.0.1:8443:127.0.0.1:32771" || true

                        ssh -f -N \
                            -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            -o ExitOnForwardFailure=yes \
                            -L 8443:127.0.0.1:32771 \
                            ${SSH_USER}@${MINIKUBE_VM}

                        echo "SSH tunnel created."

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

                        echo "========================================"
                        echo "KUBERNETES CONNECTION TEST"
                        echo "========================================"

                        export KUBECONFIG="$KUBECONFIG_FILE"

                        kubectl cluster-info

                        echo "========================================"
                        echo "KUBERNETES IDENTITY"
                        echo "========================================"

                        kubectl auth whoami

                        echo "========================================"
                        echo "RBAC TEST"
                        echo "========================================"

                        echo "Create Deployment:"
                        kubectl auth can-i create deployments

                        echo "Update Deployment:"
                        kubectl auth can-i update deployments

                        echo "Create Service:"
                        kubectl auth can-i create services

                        echo "Get Pods:"
                        kubectl auth can-i get pods
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

                        echo "========================================"
                        echo "DEPLOYING APPLICATION"
                        echo "========================================"

                        kubectl apply \
                            -f k8s/deployment.yaml

                        kubectl apply \
                            -f k8s/service.yaml

                        echo "========================================"
                        echo "UPDATING IMAGE"
                        echo "========================================"

                        kubectl set image \
                            deployment/calculator \
                            calculator=${DOCKER_IMAGE}:${DOCKER_TAG}

                        echo "========================================"
                        echo "WAITING FOR ROLLOUT"
                        echo "========================================"

                        kubectl rollout status \
                            deployment/calculator \
                            --timeout=180s

                        echo "========================================"
                        echo "DEPLOYMENT"
                        echo "========================================"

                        kubectl get deployment calculator

                        echo "========================================"
                        echo "PODS"
                        echo "========================================"

                        kubectl get pods \
                            -l app=calculator \
                            -o wide

                        echo "========================================"
                        echo "SERVICE"
                        echo "========================================"

                        kubectl get service calculator
                    '''
                }
            }
        }
    }

    post {

        always {
            sh '''
                echo "Cleaning SSH tunnel..."

                pkill -f "127.0.0.1:8443:127.0.0.1:32771" || true
            '''

            echo "Build Number: ${BUILD_NUMBER}"
        }

        success {
            echo """
            ========================================
                 PIPELINE SUCCESSFUL
            ========================================

            Application : Calculator
            Image       : ${DOCKER_IMAGE}:${DOCKER_TAG}
            Kubernetes  : Minikube
            Minikube VM : ${MINIKUBE_VM}
            ServiceAccount: jenkins-deployer

            ========================================
            """
        }

        failure {
            echo """
            ========================================
                 PIPELINE FAILED
            ========================================

            Check the failed stage above.

            ========================================
            """
        }
    }
}
