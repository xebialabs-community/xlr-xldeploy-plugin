#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from xlr_xldeploy.XLDeployClientUtil import XLDeployClientUtil
import sys

xld_client = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)

deployment = None
if xld_client.deployment_exists(deploymentPackage, environment):
    print "Upgrading deployment \n"
    deployment = xld_client.deployment_prepare_update(deploymentPackage, environment)
else:
    print "Creating initial deploy \n"
    deployment = xld_client.deployment_prepare_initial(deploymentPackage, environment)

# Mapping deployables to the target environment
# deploymentProperties + configure orchestrators
print "Mapping all deployables \n"
deployment = xld_client.deployment_prepare_deployeds(deployment, orchestrators, deployedApplicationProperties, overrideDeployedProps, deployedProperties)

print "Validating the deployment\n"
validation_messages = xld_client.validate(deployment)
if len(validation_messages) == 0:
    print "The deployment specification is valid"
else:
    for vm in validation_messages:
        print "* ERROR : %s" % vm
    print ""
    raise Exception("ERROR Validation failed")

print "Creating a deployment task \n"
taskId = xld_client.get_deployment_task_id(deployment)

print "Execute task with id: %s" % taskId
taskState = xld_client.invoke_task_and_wait_for_result(taskId, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials, failOnPause)

if displayStepLogs:
    print "Display the step logs"
    xld_client.display_step_logs(taskId)

if taskState in ('DONE', 'EXECUTED'):
    print "Deployment ended in %s \n" % taskState
    xld_client.archive_task(taskId)
    sys.exit(0)

# manage the task failure
if taskState in ('FAILED', 'STOPPED'):
    if rollbackOnError and taskState in ('FAILED', 'STOPPED'):
        print "Going to rollback \n"
        xld_client.stop_task(taskId)
        rollBackTaskId = xld_client.deployment_rollback(taskId)
        taskState = xld_client.invoke_task_and_wait_for_result(rollBackTaskId, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials)
        xld_client.archive_task(rollBackTaskId)
    elif cancelOnError:
        print "Task failed; cancelling task. \n"
        xld_client.cancel_task(taskId)
    else:
        print "Task failed; leaving as-is in XL Deploy. \n"

sys.exit(1)
