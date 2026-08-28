pipeline {

    agent any

    environment {
        DOCKER_IMAGE  = 'abhi7677/calculater'
        DOCKER_TAG    = "${BUILD_NUMBER}"

        MINIKUBE_HOST = '192.168.14.62'
        LOCAL_API_PORT = '18443'
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

                    docker build \
                        -t ${DOCKER_IMAGE}:${DOCKER_TAG} .

                    docker tag \
                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        ${DOCKER_IMAGE}:latest

                    echo "Docker build successful."
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
                        echo "CREATE SSH TUNNEL"
                        echo "========================================"

                        chmod 600 "$SSH_KEY"

                        echo "Checking local port ${LOCAL_API_PORT}..."

                        if ss -lnt | grep -q ":${LOCAL_API_PORT} "; then
                            echo "Port ${LOCAL_API_PORT} is already in use."
                            exit 1
                        fi

                        ssh -f -N \
                            -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            -o ExitOnForwardFailure=yes \
                            -L ${LOCAL_API_PORT}:127.0.0.1:32771 \
                            ${SSH_USER}@${MINIKUBE_HOST}

                        echo "SSH tunnel created successfully."

                        sleep 2

                        echo "Testing Kubernetes API..."

                        curl -k -m 10 \
                            https://127.0.0.1:${LOCAL_API_PORT}/version

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

                        echo "========================================"
                        echo "KUBERNETES CONNECTION"
                        echo "========================================"

                        kubectl cluster-info

                        echo "========================================"
                        echo "KUBERNETES IDENTITY"
                        echo "========================================"

                        kubectl auth whoami

                        echo "========================================"
                        echo "RBAC CHECK"
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

                        echo "========================================"
                        echo "DEPLOY APPLICATION"
                        echo "========================================"

                        kubectl apply \
                            -f k8s/deployment.yaml

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
            echo "Cleaning SSH tunnel..."

            sh '''
                TUNNEL_PID=$(pgrep -f \
                    "ssh.*-L ${LOCAL_API_PORT}:127.0.0.1:32771" \
                    || true)

                if [ -n "$TUNNEL_PID" ]; then
                    echo "Stopping SSH tunnel: $TUNNEL_PID"
                    kill $TUNNEL_PID || true
                fi
            '''

            echo "Build Number: ${BUILD_NUMBER}"
        }

        success {
            echo """
============================================
       PIPELINE SUCCESSFUL
============================================

Application    : Calculator
Docker Image   : ${DOCKER_IMAGE}:${DOCKER_TAG}
Minikube VM    : ${MINIKUBE_HOST}
Kubernetes SA  : jenkins-deployer

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
    }
}
