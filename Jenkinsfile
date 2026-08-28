
The actual file should start directly like this:

:::writing{variant="document" id="74126"}
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

                    docker push ${DOCKER_IMAGE}:${DOCKER_TAG}

                    docker tag \
                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        ${DOCKER_IMAGE}:latest

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
:::

**Important:** When copying the above into GitHub, copy only the content starting with `pipeline {` and ending with `}`. Do not add Markdown ``` characters.

After committing the corrected Jenkinsfile, run **Build Now** again. Your pipeline should get past the Groovy compilation stage and proceed to Docker build/login.
