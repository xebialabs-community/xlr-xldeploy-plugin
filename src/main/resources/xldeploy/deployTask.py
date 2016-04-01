#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
from xldeploy.XLDeployClientUtil import XLDeployClientUtil
import sys

xldClient = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)

deployment = None
if xldClient.deployment_exists(deploymentPackage, environment):
    print "Upgrading deployment \n"
    deployment = xldClient.deploymentPrepareUpdate(deploymentPackage,environment)
else:
    print "Creating initial deploy \n"
    deployment = xldClient.deploymentPrepareInitial(deploymentPackage, environment)

# Mapping deployables to the target environment
# deploymentProperties + configure orchestrators
print "Mapping all deployables \n"
deployment = xldClient.deployment_prepare_deployeds(deployment, orchestrators, deployedApplicationProperties, deployedProperties)

print"Validating the deployment\n"
validation_messages = xldClient.validate(deployment)
if len(validation_messages) == 0:
    print "The deployment specification is valid"
else:
    for vm in validation_messages:
        print "* ERROR : %s" % vm
    print ""
    raise Exception("ERROR Validation failed")

print "Creating a deployment task \n"
taskId = xldClient.get_deployment_task_id(deployment)

print "Execute task with id: %s" % taskId
taskState = xldClient.invoke_task_and_wait_for_result(taskId, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials, failOnPause)

xldClient.display_step_logs(taskId)

if taskState in ('DONE', 'EXECUTED'):
    print "Deployment ended in %s \n" % taskState
    xldClient.archive_task(taskId)
    sys.exit(0)

# manage the task failure
if taskState in ('FAILED', 'STOPPED'):
    if rollbackOnError and taskState in ('FAILED', 'STOPPED'):
        print "Going to rollback \n"
        xldClient.stop_task(taskId)
        rollBackTaskId = xldClient.deployment_rollback(taskId)
        taskState = xldClient.invoke_task_and_wait_for_result(rollBackTaskId, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials)
        xldClient.archive_task(rollBackTaskId)
    else:
        print "Task failed, rollback not enabled. \n"
        xldClient.cancel_task(taskId)

sys.exit(1)
