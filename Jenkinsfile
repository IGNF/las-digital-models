parallel (

	"conda":{
	node('linux_conda') {

		stage('init') {
		gitlabCommitStatus("init") {
			checkout scm
		}
		}

		stage('mamba') {
		gitlabCommitStatus("mamba") {
			sh "mamba env update -n produits_derives_lidar"
		}
		}

		stage('test') {
		gitlabCommitStatus("test") {
			sh "mamba run -n produits_derives_lidar ./run_tests.sh"
		}
		}

	}
	},

	"docker":{	
	node('DOCKER') {

		stage('docker-build') {
			gitlabCommitStatus("docker-build") {
				if (env.BRANCH_NAME == 'master') {
					checkout scm
					sh "cd docker && ./build.sh"
				} else {
					echo "Nothing to do, because branch is not master"
				}
			}
		}

        //
		// stage('docker-test') {
		// 	gitlabCommitStatus("docker-test") {
		// 		if (env.BRANCH_NAME == 'master') {
		// 			sh "./docker/test_docker_image.sh"
		// 		} else {
		// 			echo "Nothing to do, because branch is not master"
		// 		}
		// 	}
		// }

        stage('docker-deploy') {
			gitlabCommitStatus("docker-deploy") {

				if (env.BRANCH_NAME == 'master') {
					withCredentials([string(credentialsId: 'svc_lidarhd', variable: 'svc_lidarhd')]) {
						sh "./docker/deploy-jenkins.sh ${svc_lidarhd}"
					}
				} else {
					echo "Nothing to do, because branch is not master"
				}

			}
		}

	}
	}
)