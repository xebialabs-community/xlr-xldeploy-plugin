#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from xldeploy.XLDeployClientUtil import XLDeployClientUtil

xldClient = XLDeployClientUtil.createXLDeployClient(xldeployServer, username, password)

deployment = None
if xldClient.deployment_exists(deploymentPackage, environment):
    print "Upgrading deployment \n"
    deployment = xldClient.deploymentPrepareUpdate(deploymentPackage,environment)
else:
    print "Creating initial deploy \n"
    deployment = xldClient.deploymentPrepareInitial(deploymentPackage, environment)

# Mapping deployables to the target environment
print "Mapping all deployables \n"
deployment = xldClient.deployment_prepare_deployeds(deployment, orchestrators, deployedApplicationProperties, deployedProperties)

# deploymentProperties + configure orchestrators
# print "DEBUG: Deployment description is now: %s" % deployment
# Validating the deployment
print "Creating a deployment task \n"
taskId = xldClient.get_deployment_task_id(deployment)

print "Execute task with id: %s" % taskId
taskState = xldClient.invoke_task_and_wait_for_result(taskId, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials, failOnPause)

xldClient.display_step_logs(taskId)

if taskState in ('DONE','EXECUTED'):
    print "Deployment ended in %s \n" % taskState
    xldClient.archive_task(taskId)
    sys.exit(0)

# rollbackOnError
if rollbackOnError and taskState in ('FAILED', 'STOPPED'):
    print "Going to rollback \n"
    xldClient.stop_task(taskId)
    rollBackTaskId = xldClient.deployment_rollback(taskId)
    taskState = xldClient.invoke_task_and_wait_for_result(rollBackTaskId, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials)
    xldClient.archive_task(rollBackTaskId)
    sys.exit(1)
elif taskState in ('FAILED', 'STOPPED'):
    print "Task failed, rollback not enabled. \n"
    xldClient.cancel_task(taskId)
    sys.exit(1)
