#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from xldeploy.XLDeployClientUtil import XLDeployClientUtil

xldClient = XLDeployClientUtil.createXLDeployClient(xldeployServer, username, password)

taskState = xldClient.wait_for_result(xldTaskId, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials, failOnPause)

xldClient.displayStepLogs(xldTaskId)

if taskState in ('DONE','EXECUTED'):
    print "Deployment ended in %s \n" % taskState
    xldClient.archiveTask(xldTaskId)
    sys.exit(0)

# rollbackOnError
if rollbackOnError and taskState in ('FAILED', 'STOPPED'):
    print "Going to rollback \n"
    xldClient.stopTask(xldTaskId)
    rollBackTaskId = xldClient.deploymentRollback(xldTaskId)
    taskState = xldClient.invoke_task_and_wait_for_result(rollBackTaskId, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials)
    xldClient.archiveTask(rollBackTaskId)
    sys.exit(1)
elif taskState in ('FAILED', 'STOPPED'):
    print "Task failed, rollback not enabled. \n"
    xldClient.cancelTask(xldTaskId)
    sys.exit(1)
