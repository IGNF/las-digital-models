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
			sh """
			mamba run -n produits_derives_lidar make testing
			"""
		}
		}
		stage('deploy') {
		gitlabCommitStatus("pip-deploy") {
			if (env.BRANCH_NAME == 'master') {
				withCredentials([string(credentialsId: 'svc_lidarhd', variable: 'svc_lidarhd')]) {
					sh """
					set -e
					mamba run -n produits_derives_lidar make build
					mamba run -n produits_derives_lidar make svc_lidarhd_pwd=${svc_lidarhd} deploy-w-creds
					"""
				}
			} else {
				echo "Nothing to do, because branch is not master"
			}
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
					sh "make docker-build"
				} else {
					echo "Nothing to do, because branch is not master"
				}
			}
		}

		stage('docker-test') {
			gitlabCommitStatus("docker-test") {
				if (env.BRANCH_NAME == 'master') {
					sh "make docker-test"
				} else {
					echo "Nothing to do, because branch is not master"
				}
			}
		}

        stage('docker-deploy') {
			gitlabCommitStatus("docker-deploy") {

				if (env.BRANCH_NAME == 'master') {
					withCredentials([string(credentialsId: 'svc_lidarhd', variable: 'svc_lidarhd')]) {
						sh "make svc_lidarhd_pwd=${svc_lidarhd} docker-deploy-w-creds"
					}
				} else {
					echo "Nothing to do, because branch is not master"
				}

			}
		}

	}
	}
)