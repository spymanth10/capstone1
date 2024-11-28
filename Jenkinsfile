pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'head-detection-app'
        DOCKER_TAG = "${GIT_BRANCH.toLowerCase().replace('/', '-')}-${GIT_COMMIT.substring(0,7)}"
        GITHUB_REPO = 'your-username/head-detection-app'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh '. venv/bin/activate && pytest tests/'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    // Example deployment to a test server
                    sh """
                        docker stop head-detection-app || true
                        docker rm head-detection-app || true
                        docker run -d \
                            --name head-detection-app \
                            -p 5000:5000 \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }
    }
    
    post {
        failure {
            emailext (
                subject: "Jenkins Build Failed: ${currentBuild.fullDisplayName}",
                body: """
                    Build Failed: ${env.JOB_NAME} 
                    Build Number: ${env.BUILD_NUMBER}
                    Build URL: ${env.BUILD_URL}
                    
                    Check console output at ${env.BUILD_URL}console
                """,
                to: 'your-email@example.com',
                from: 'jenkins@yourdomain.com'
            )
        }
        
        success {
            emailext (
                subject: "Jenkins Build Successful: ${currentBuild.fullDisplayName}",
                body: """
                    Build Successful: ${env.JOB_NAME}
                    Build Number: ${env.BUILD_NUMBER}
                    Build URL: ${env.BUILD_URL}
                    
                    Docker Image: ${DOCKER_IMAGE}:${DOCKER_TAG}
                """,
                to: 'your-email@example.com',
                from: 'jenkins@yourdomain.com'
            )
        }
    }
}