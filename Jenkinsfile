pipeline {

    agent any

    environment {
        DOCKER_IMAGE = 'abhi7677/calculater'
        DOCKER_TAG   = "${BUILD_NUMBER}"

        MINIKUBE_HOST = '192.168.14.62'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out application source...'

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
                    echo "BUILD DOCKER IMAGE"
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

        stage('Push Docker Image') {
            steps {
                sh '''
                    set -e

                    echo "========================================"
                    echo "PUSH DOCKER IMAGE"
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
                        echo "CREATE SSH TUNNEL"
                        echo "========================================"

                        chmod 600 "$SSH_KEY"

                        # Clean any old tunnel created by this job
                        pkill -f "ssh.*-L 8443:127.0.0.1:32771" || true

                        ssh -f -N \
                            -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            -o ExitOnForwardFailure=yes \
                            -L 8443:127.0.0.1:32771 \
                            ${SSH_USER}@${MINIKUBE_HOST}

                        sleep 2

                        echo "SSH tunnel created."

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

                        echo "========================================"
                        echo "UPDATE IMAGE"
                        echo "========================================"

                        kubectl set image \
                            deployment/calculator \
                            calculator=${DOCKER_IMAGE}:${DOCKER_TAG}

                        echo "========================================"
                        echo "ROLLOUT"
                        echo "========================================"

                        kubectl rollout status \
                            deployment/calculator \
                            --timeout=180s

                        echo "========================================"
                        echo "DEPLOYMENT STATUS"
                        echo "========================================"

                        kubectl get deployment calculator

                        echo "========================================"
                        echo "POD STATUS"
                        echo "========================================"

                        kubectl get pods \
                            -l app=calculator \
                            -o wide

                        echo "========================================"
                        echo "SERVICE STATUS"
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
                pkill -f "ssh.*-L 8443:127.0.0.1:32771" || true
            '''

            echo "Build Number: ${BUILD_NUMBER}"
        }

        success {
            echo """
============================================
       PIPELINE SUCCESSFUL
============================================

Application       : Calculator
Docker Image      : ${DOCKER_IMAGE}:${DOCKER_TAG}
Minikube VM       : ${MINIKUBE_HOST}
Kubernetes SA     : jenkins-deployer

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
