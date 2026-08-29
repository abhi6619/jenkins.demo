pipeline {

    agent any

    environment {
        GIT_REPO = 'http://github.com/abhi6619/jenkins.demo'
        GIT_BRANCH = 'main'

        DOCKER_IMAGE = 'abhi7677/calculater'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout Source Code') {
            steps {
                echo "Checking out source code from GitHub..."

                git branch: "${GIT_BRANCH}",
                    url: "${GIT_REPO}"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh """
                        echo "Building Docker image..."

                        docker build \
                          -t ${DOCKER_IMAGE}:${IMAGE_TAG} \
                          .

                        docker tag \
                          ${DOCKER_IMAGE}:${IMAGE_TAG} \
                          ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "Logging in to Docker Hub..."

                        echo "$DOCKER_PASSWORD" | docker login \
                          -u "$DOCKER_USERNAME" \
                          --password-stdin
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sh """
                    echo "Pushing image with build number..."

                    docker push ${DOCKER_IMAGE}:${IMAGE_TAG}

                    echo "Pushing latest image..."

                    docker push ${DOCKER_IMAGE}:latest
                """
            }
        }
    }

    post {

        success {
            echo "=========================================="
            echo "PIPELINE SUCCESSFUL"
            echo "=========================================="
            echo "Docker Image: ${DOCKER_IMAGE}:${IMAGE_TAG}"
            echo "Docker Image: ${DOCKER_IMAGE}:latest"
        }

        failure {
            echo "=========================================="
            echo "PIPELINE FAILED"
            echo "=========================================="
        }

        always {
            sh '''
                echo "Cleaning up unused Docker images..."

                docker image prune -f || true
            '''
        }
    }
}
