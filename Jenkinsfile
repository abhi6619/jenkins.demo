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
        withCredentials([
            file(
                credentialsId: 'jenkins-deployer',
                variable: 'KUBECONFIG_FILE'
            )
        ]) {
            sh '''
                set -e

                echo "======================================"
                echo "Kubernetes Connection"
                echo "======================================"

                export KUBECONFIG="$KUBECONFIG_FILE"

                kubectl cluster-info

                echo "======================================"
                echo "Current Kubernetes Identity"
                echo "======================================"

                kubectl auth whoami

                echo "======================================"
                echo "Deploying Application"
                echo "======================================"

                kubectl apply -f k8s/deployment.yaml
                kubectl apply -f k8s/service.yaml

                echo "======================================"
                echo "Updating Image"
                echo "======================================"

                kubectl set image deployment/calculator \
                    calculator=${DOCKER_IMAGE}:${DOCKER_TAG}

                echo "======================================"
                echo "Waiting for Rollout"
                echo "======================================"

                kubectl rollout status deployment/calculator \
                    --timeout=180s

                echo "======================================"
                echo "Final Status"
                echo "======================================"

                kubectl get deployment calculator
                kubectl get pods -l app=calculator
                kubectl get service calculator
            '''
        }
    }
}
