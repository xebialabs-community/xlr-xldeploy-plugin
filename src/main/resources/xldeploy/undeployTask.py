#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys
from xldeploy.XLDeployClientUtil import XLDeployClientUtil

xld_client = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)

deployment = None
deployment_package = xld_client.get_deployment_package("%s/%s" % (environment, deployedApplication))
if xld_client.deployment_exists(deployment_package, environment):
    print "Undeploying [%s] from environment [%s] \n" % (deployment_package, environment)
    deployment = xld_client.deployment_prepare_undeploy("%s/%s" % (environment, deployedApplication), orchestrators, deployedApplicationProperties)
else:
    print "No deployed application found [%s] for environment [%s] \n" % (deployedApplication, environment)
    sys.exit(1)

print "Creating a deployment task \n"
task_id = xld_client.get_deployment_task_id(deployment)

print "Execute task with id: %s" % task_id
task_state = xld_client.invoke_task_and_wait_for_result(task_id, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials, failOnPause)

xld_client.display_step_logs(task_id)

if task_state in ('DONE','EXECUTED'):
    print "Deployment ended in %s \n" % task_state
    xld_client.archive_task(task_id)
    sys.exit(0)

# rollbackOnError
if rollbackOnError and task_state in ('FAILED', 'STOPPED'):
    print "Going to rollback \n"
    xld_client.stop_task(task_id)
    rollback_task_id = xld_client.deployment_rollback(task_id)
    task_state = xld_client.invoke_task_and_wait_for_result(rollback_task_id, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials)
    xld_client.archive_task(rollback_task_id)
    sys.exit(1)
elif task_state in ('FAILED', 'STOPPED'):
    if cancelOnError:
        print "Task failed; cancelling task. \n"
        xld_client.cancel_task(task_id)
    else:
        print "Task failed; leaving as-is in XL Deploy. \n"
    sys.exit(1)
