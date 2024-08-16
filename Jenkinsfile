@Library('slack') _

pipeline {
  agent any

  environment {
    DOCKER_IMAGE = "gauss022/dua_auth:${GIT_COMMIT}"
    MANIFEST_REPO = "https://github.com/Teksseract/dua_ms_auth.git"
    MANIFEST_REPO_2 = "github.com/Teksseract/dua_ms_auth.git"
    GIT_BRANCH = "main"
    K8S_MANIFEST_PATH = "k8s_manifest/deployment.yaml"
    SERVICE_NAME = "dua-auth-service"
    DEPLOYMENT_NAME = "dua-auth"
    CONTAINER_NAME = "dua-auth"
  }

  stages {
    stage('Checkout') {
      steps {
        deleteDir() // Clean the workspace
        checkout scm
      }
    }
    // stage ('Static Analysis') {
    //   parallel {
    //     stage('SCA'){
    //        when {
    //         expression { BRANCH_NAME == 'main' }
    //       }

    //       steps{
    //         // catchError(buildResult:'SUCCESS',stageResult:'FAILURE'){
    //           dir('simple_java_app/'){
    //             sh'mvn org.owasp:dependency-check-maven:check'
    //         //  }
    //         }
    //       }
    //       post {
    //         always {
    //           archiveArtifacts allowEmptyArchive: true, artifacts:'simple_java_app/target/dependency-check-report.html', fingerprint: true, onlyIfSuccessful: false
    //           dependencyCheckPublisher pattern: 'simple_java_app/target/dependency-check-report.xml'
    //         }
    //       }
    //     }
        
    //     stage('Unit Tests') {
    //       when {
    //         expression { BRANCH_NAME == 'main' }
    //       }

    //       steps {
    //         dir('simple_java_app/'){
    //           sh "mvn test"
    //         }
    //       }
    //       post {
    //         always {
    //           junit testResults: '**/simple_java_app/target/surefire-reports/*.xml'
    //           jacoco execPattern: 'simple_java_app/target/jacoco.exec'
    //         }
    //       }
    //     }
    //     stage('Sonarqube - SAST') {
    //       when {
    //         expression { BRANCH_NAME == 'main'}
    //       }

    //       steps {
    //         dir('simple_java_app') {
    //           withSonarQubeEnv('sonar') {
    //             sh "mvn verify sonar:sonar \
    //                   -Dsonar.projectKey=numeric-app \
    //                   -Dsonar.projectName='numeric-app' \
    //                   -Dsonar.host.url=https://sonar.devgauss.com"
    //           }
    //           timeout(time: 2, unit: 'MINUTES') {
    //             script {
    //               waitForQualityGate abortPipeline: true
    //             }
    //           }
    //         }
    //       }
    //     }

    //   }
    // }
    // stage('Mutation Tests') {
    //   when {
    //     expression { BRANCH_NAME == 'main' }
    //   }

    //   steps {
    //     dir('simple_java_app/'){
    //       sh "mvn org.pitest:pitest-maven:mutationCoverage"
    //     }
    //   }
    //   post {
    //     always {
    //       pitmutation mutationStatsFile: '**/simple_java_app/target/pit-reports/**/mutations.xml'
    //     }
    //   }
    // }
    stage ('Image Analysis') {
      parallel {
        stage ('Base Image Scan') {
          when {
            expression { BRANCH_NAME == 'main' }
          }

          steps {
            sh "bash ./trivy-base-image-scan.sh"
          }
        }
        stage ('OPA Conftest') {
          steps {
            sh 'docker run --rm  -v $(pwd):/project openpolicyagent/conftest test --policy opa-docker-security.rego ./Dockerfile'
          }  
        }
      }
    }
    stage('Docker build and push') {
      when {
        expression { BRANCH_NAME == 'main' }
      }

      steps {
        script {
            withDockerRegistry([credentialsId: 'docker-hub', url: '']) {
              sh "docker build -t ${env.DOCKER_IMAGE} ."
              sh "docker push ${env.DOCKER_IMAGE}"
          }
        }
      }
    }
    stage ('Scan K8s Manifest') {
      parallel {
        stage ('OPA Scan') {
          steps {
            sh 'docker run --rm  -v $(pwd):/project openpolicyagent/conftest test --policy opa-k8s-security.rego ./k8s_manifest/deployment.yaml'
            sh 'docker run --rm  -v $(pwd):/project openpolicyagent/conftest test --policy opa-k8s-security.rego ./k8s_manifest/service.yaml'
            sh 'docker run --rm  -v $(pwd):/project openpolicyagent/conftest test --policy opa-k8s-security.rego ./k8s_manifest/ingress.yaml'
          }
        }
        stage ('Kubesec Scan - Deploy') {
          steps {
            sh 'bash ./kubesec-scan-deploy.sh'
          }
        }
        stage ('Trivy Scan') {
          steps {
            sh 'bash ./trivy-k8s-image-scan.sh'
          }
        }
      }
    }
    stage ('Deploy to Dev') {
      parallel {
        stage('Checkout Manifest Repository') {
          steps {
            git branch: "${env.GIT_BRANCH}", url: "${env.MANIFEST_REPO}", credentialsId: 'github-token'
          }
        }

        stage('Update K8s Manifests') {
          when {
            expression { BRANCH_NAME == 'main' }
          }

          steps {
            script {
              withCredentials([usernamePassword(credentialsId: 'github-token', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                sh 'git config --global user.email "jenkins@example.com"'
                sh 'git config --global user.name "jenkins"'
                sh "git remote set-url origin https://${USER}:${PASS}@${env.MANIFEST_REPO_2}"
                sh "git pull origin ${env.GIT_BRANCH}"
                sh "sed -i 's|image: .*|image: ${env.DOCKER_IMAGE}|' ${env.K8S_MANIFEST_PATH}"
                sh "git add ."
                sh "git commit -m 'Update image to latest'"
                sh "git push origin ${env.GIT_BRANCH}"
              }
            }
          }
        }
      }
    }
    // stage ('DAST') {
    //   parallel {
    //     stage ('OWASP ZAP') {
    //       steps {
    //         sh 'bash zap.sh'
    //       }
          
    //       post {
    //         always {
    //           publishHTML([allowMissing: false, alwaysLinkToLastBuild: true, keepAll: true, reportDir: 'owasp-zap-report', reportFiles: 'zap_report.html', reportName: 'OWASP ZAP HTML Report', reportTitles: 'OWASP ZAP HTML Report', useWrapperFileDirectly: true])
    //         }
    //       }
    //     }
    //   }
    // }

    // stage ("Do to Pre-Prod") {
    //   steps {
    //     timeout(time: 2, unit: 'DAYS') {
    //       input 'Do you want to Approve to the Deployment to Pre-Prod Environment/Namespace?'
    //     }
    //   }
    // }
    
  }
  // post {
  //   always {
  //     slack_notification currentBuild.result
  //   }
  // }
}
