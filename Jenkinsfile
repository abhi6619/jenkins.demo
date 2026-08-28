pipeline {

    agent any

    environment {
        DOCKER_IMAGE = "abhi7677/calculater"
        KUBE_SERVER  = "https://127.0.0.1:18443"
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
                    docker build \
                        -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .

                    docker tag \
                        ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                        ${DOCKER_IMAGE}:latest
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
                        echo "$DOCKER_PASSWORD" | docker login \
                            -u "$DOCKER_USER" \
                            --password-stdin
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sh '''
                    docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    docker push ${DOCKER_IMAGE}:latest
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

                        ssh \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            -o ExitOnForwardFailure=yes \
                            -i "$SSH_KEY" \
                            -N \
                            -L 18443:127.0.0.1:32771 \
                            ${SSH_USER}@192.168.14.62 &

                        SSH_TUNNEL_PID=$!

                        echo "$SSH_TUNNEL_PID" \
                            > "$WORKSPACE/ssh_tunnel.pid"

                        sleep 2

                        echo "Testing Kubernetes API..."

                        curl -k -m 10 \
                            ${KUBE_SERVER}/version

                        echo ""
                        echo "Kubernetes API is reachable."
                    '''
                }
            }
        }

        stage('Kubernetes Authentication') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'jenkins-deployer',
                        variable: 'KUBE_TOKEN'
                    )
                ]) {
                    sh '''
                        set -e

                        export KUBECONFIG="$WORKSPACE/kubeconfig"

                        kubectl config set-cluster minikube \
                            --server=${KUBE_SERVER} \
                            --insecure-skip-tls-verify=true

                        kubectl config set-credentials jenkins-deployer \
                            --token="$KUBE_TOKEN"

                        kubectl config set-context minikube \
                            --cluster=minikube \
                            --user=jenkins-deployer \
                            --namespace=default

                        kubectl config use-context minikube

                        echo "========================================"
                        echo "KUBERNETES CONNECTION"
                        echo "========================================"

                        kubectl cluster-info

                        echo ""
                        echo "ServiceAccount:"
                        kubectl auth whoami || true

                        echo ""
                        echo "Permissions:"
                        kubectl auth can-i get pods
                        kubectl auth can-i create deployments
                        kubectl auth can-i create services
                    '''
                }
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    set -e

                    export KUBECONFIG="$WORKSPACE/kubeconfig"

                    echo "Deploying Calculator application..."

                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl set image deployment/calculator \
                        calculator=${DOCKER_IMAGE}:${BUILD_NUMBER}

                    kubectl rollout status \
                        deployment/calculator \
                        --timeout=180s

                    echo ""
                    echo "========================================"
                    echo "DEPLOYMENT SUCCESSFUL"
                    echo "========================================"

                    kubectl get pods
                    kubectl get svc calculator
                '''
            }
        }
    }

    post {
        always {
            sh '''
                if [ -f "$WORKSPACE/ssh_tunnel.pid" ]; then

                    PID=$(cat "$WORKSPACE/ssh_tunnel.pid")

                    echo "Stopping SSH tunnel PID: $PID"

                    kill "$PID" 2>/dev/null || true

                    rm -f "$WORKSPACE/ssh_tunnel.pid"
                fi

                rm -f "$WORKSPACE/kubeconfig"
            '''

            echo "Build Number: ${BUILD_NUMBER}"
        }

        success {
            echo "============================================"
            echo "          PIPELINE SUCCESS"
            echo "============================================"
        }

        failure {
            echo "============================================"
            echo "          PIPELINE FAILED"
            echo "============================================"
        }
    }
}
