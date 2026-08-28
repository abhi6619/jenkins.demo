```groovy
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "abhi7677/calculater"
        DOCKER_TAG   = "${BUILD_NUMBER}"
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
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                '''
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -e

                        echo "$DOCKER_PASSWORD" | docker login \
                            --username "$DOCKER_USERNAME" \
                            --password-stdin
                    '''
                }
            }
        }

        stage('Push Image') {
            steps {
                sh '''
                    set -e

                    # Push build-specific image
                    docker push ${DOCKER_IMAGE}:${DOCKER_TAG}

                    # Tag the same image as latest
                    docker tag \
                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        ${DOCKER_IMAGE}:latest

                    # Push latest
                    docker push ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    set -e

                    kubectl apply -f k8s/deployment.yaml -n calculator
                    kubectl apply -f k8s/service.yaml -n calculator

                    kubectl -n calculator set image deployment/calculator \
                        calculator=${DOCKER_IMAGE}:${DOCKER_TAG}

                    kubectl -n calculator rollout status \
                        deployment/calculator
                '''
            }
        }
    }

    post {
        success {
            echo "================================="
            echo "Application deployed successfully"
            echo "Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
            echo "================================="
        }

        failure {
            echo "================================="
            echo "Pipeline failed!"
            echo "================================="
        }
    }
}
```
