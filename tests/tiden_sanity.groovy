// Constants as environment fields
env.TIDEN_PKG_REPO = "https://github.com/mshonichev/tiden_pkg.git"
env.TIDEN_GG_PKG_REPO = "https://github.com/mshonichev/tiden_gridgain_pkg.git"
env.TIDEN_GG_SUITES__REPO = ""

env.TIDEN_PKG_CHECKOUT_DIR = "gridgain/tiden"
env.TIDEN_GG_PKG_CHECKOUT_DIR = "ggprivate/tiden_gridgain_pkg"
env.TIDEN_GG_SUITES_CHECKOUT_DIR = "ggprivate/tiden-gridgain-suites"

env.GITHUB_CREDENTIALS_ID = "0cc82f1a-e7dc-4db2-9774-7adfbd238b9b"
env.QA_FTP_CONFIG_FILE_ID = "6fbbc991-7e18-40d3-a1b3-090fbc4dbe19"

CLEAN_UP_JOB = 'utils/clean-java-processes'

taskParams = []

configsToPatch = [
        "config/artifacts-gg-ult-fab.yaml",
        "config/artifacts-piclient.yaml"
]

// Pipeline properties
properties([
        [$class: 'GithubProjectProperty', projectUrlStr: 'https://github.com/mshonichev/tiden_pkg.git'],

        buildDiscarder(
                logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '', numToKeepStr: '10')
        ),

        parameters([
                string(name: 'IGNITE_VERSION', defaultValue: '8.7.24',
                        description: 'Apache Ignite version, ex. 2.5.1'),
                string(name: 'GRIDGAIN_VERSION', defaultValue: '8.7.24',
                        description: 'GridGain version, ex. 8.5.1'),
                string(name: 'HOSTS', defaultValue: '172.25.1.1',
                        description: 'IP for server hosts, ex. "1.1.1.1-10,1.1.1.11" will be used 11 hosts'),
                string(name: 'TIDEN_PKG_BRANCH', defaultValue: 'master',
                        description: 'Branch in the gridgain/tiden repo.'),
                string(name: 'TIDEN_GG_PKG_BRANCH', defaultValue: 'master',
                        description: 'Branch in the ggprivate/tiden_gridgain_pkg repo.'),
                string(name: 'TIDEN_GG_SUITES_BRANCH', defaultValue: 'master',
                        description: 'Branch in the ggprivate/tiden-gridgain-suites repo.')
        ])
])

// Pipeline stages
node {
    stage("Clean-up") {
        cleanWs()
    }
    stage("Checkout") {
        // Checkout Tiden from git
/*        checkout poll: false, scm: [
                $class: 'GitSCM',
                branches: [[name: params.TIDEN_GG_SUITES_BRANCH]],
                doGenerateSubmoduleConfigurations: false,
                extensions: [
                        [$class: 'RelativeTargetDirectory', relativeTargetDir: env.TIDEN_GG_SUITES_CHECKOUT_DIR],
                        [$class: 'CleanBeforeCheckout']
                ],
                submoduleCfg: [],
                userRemoteConfigs: [
                        [credentialsId: env.GITHUB_CREDENTIALS_ID, url: env.TIDEN_GG_SUITES_REPO]
                ]
        ]*/
        checkout poll: false, scm: [
                $class: 'GitSCM',
                branches: [[name: params.TIDEN_PKG_BRANCH]],
                doGenerateSubmoduleConfigurations: false,
                extensions: [
                        [$class: 'RelativeTargetDirectory', relativeTargetDir: env.TIDEN_PKG_CHECKOUT_DIR],
                        [$class: 'CleanBeforeCheckout']
                ],
                submoduleCfg: [],
                userRemoteConfigs: [
                        [credentialsId: env.GITHUB_CREDENTIALS_ID, url: env.TIDEN_PKG_REPO]
                ]]
/*        checkout poll: false, scm: [
                $class: 'GitSCM',
                branches: [[name: params.TIDEN_GG_PKG_BRANCH]],
                doGenerateSubmoduleConfigurations: false,
                extensions: [
                        [$class: 'RelativeTargetDirectory', relativeTargetDir: env.TIDEN_GG_PKG_CHECKOUT_DIR],
                        [$class: 'CleanBeforeCheckout']
                ],
                submoduleCfg: [],
                userRemoteConfigs: [
                        [credentialsId: env.GITHUB_CREDENTIALS_ID, url: env.TIDEN_GG_PKG_REPO]
                ]]*/
    }

    stage("Prepare") {
        // Prepare directories
        fileOperations([
                folderDeleteOperation('work'),
                folderDeleteOperation('var'),
                folderDeleteOperation('.venv'),
                folderCreateOperation('work'),
                folderCreateOperation('var')
                folderCreateOperation('.venv')
        ])

        dir(env.TIDEN_GG_PKG_CHECKOUT_DIR) {
            // Prepare Python venv
            stage("Init venv") {
                withEnv(["PYTHON_UNBUFFERED=1"]) {
                    sh script: '''#!/usr/bin/env bash
set -e
python3 --version
pip3 --version
python3 -m venv .venv
source .venv/bin/activate
pip --version

pip install -U pytest
pip install -r requirements.txt
'''
                }
            }
            stage("Run unit tests") {
                withEnv(["PYTHON_UNBUFFERED=1"]) {
                    sh script: '''#!/usr/bin/env bash
set -e
source .venv/bin/activate
py.test tests -x
'''
                }
            }
/*
            stage("Prepare work dir") {
                // Get artifacts for testing
                configFileProvider([configFile(
                        fileId: env.QA_FTP_CONFIG_FILE_ID,
                        targetLocation: "${env.WORKSPACE}/qa_ftp.yaml"
                )]) {
                    echo "Prepare working directory for ${IGNITE_VERSION}/${GRIDGAIN_VERSION}"
                    sh script: '''#!/usr/bin/env bash
set -e
export DIST_SOURCE='gridgain-ultimate'
bash \\
    utils/prepare_work_dir.sh \\
        --work-dir=$WORKSPACE/work \\
        --var-dir=$WORKSPACE/var \\
        --config=$WORKSPACE/qa_ftp.yaml \\
'''
                }
            }

            configsToPatch.each { configPath ->
                configContent = readFile(configPath)
                echo "Patch $configPath"
                configContent = configContent.replaceAll("\\./work", "${env.WORKSPACE}/work")
                writeFile(file: configPath, text: configContent)
            }*/
        }
    }

/*    stage("Run") {
//        Map tasks = prepareTasks()
        echo "All tasks $tasks"
//        parallel(tasks)
    }*/
}

/*
Map prepareTasks() {
    hosts = []
    (params.HOSTS.tokenize(",")).each { host ->
        if (host.contains('-')) {
            separatedHost = host.tokenize('-')
            startIp = separatedHost[0]
            endHost = separatedHost[1]
            ipBlocks = startIp.tokenize('.')
            lastIpBlock = ipBlocks[-1]
            (lastIpBlock.toInteger()..endHost.toInteger()).each { hostNum ->
                hosts += (ipBlocks[0..-2] + hostNum).join('.')
            }
        } else {
            hosts += host
        }
    }

    nodesCount = params.NODES_COUNT.toInteger()
    nodesOnHost = params.NODES_ON_HOST.toInteger()
    hostsNeeded = nodesCount / nodesOnHost
    hosts = hosts.collate(hostsNeeded.intValue())

    // Sort by keys
    Map tasks = [:]
    hosts.each { hostsPool ->
        if (hostsPool.size() != hostsNeeded) {
            return
        }
        def hostNumbers = hostsPool.collect { ip -> ip.tokenize('.')[-1].toInteger() }
        def runName = hostNumbers.join(' ')
        tasks[runName] = {
            stage(runName) {
                echo "params inside stage: $params"
                def pool = hostsPool
                def poolStr = pool.join(',')
                def name = runName
                echo "separated params: $pool, $poolStr, $name"
                def runCmd = [
                        "bash ./venv-run-tiden.sh run-tests",
                        "--ts=combine",
                        "--tc=config/env_jenkins.yaml",
                        "--tc=config/jenkins-combine.yaml",
                        "--tc=config/artifacts-gg-ult-fab.yaml",
                        "--tc=config/artifacts-piclient.yaml",
                        "--clean=all",
                        "--var_dir=${env.WORKSPACE}/var/${name.replaceAll(' ', '_')}",
                        "--to=environment.server_hosts=$poolStr",
                        "--to=environment.client_hosts=$poolStr",
                        "--to=environment.servers_per_host=$nodesOnHost",
                        "--to=combinations.parallel_type=${params.CODE.size() == 0 ? "worker" : "standalone"}",
                        params.CODE.size() == 0 ? "--to=combinations.seed=$params.SEED" : "--to=combinations.code=$params.CODE",
                ].join(' ')
                echo "separated params after run string: $pool, $poolStr, $name"
                echo "Run: $runCmd"
                // Run the suite
                echo "Start workers ${name}"
                // Run Tiden
                dir(env.TIDEN_GG_SUITES_CHECKOUT_DIR) {
                    try {
                        stage('Exec') {
                            sh runCmd
                        }
                    } finally {
                        stage("Clean-up") {
                            cleanWs()
                        }
                        stage('Teardown') {
                            build job: CLEAN_UP_JOB, parameters: [
                                    string(name: 'HOSTS', value: poolStr),
                            ]
                        }
                    }

                }
                echo "All workers started ${name}"
            }
        }
    }
    echo "All params: $taskParams"
    return tasks
}
*/

