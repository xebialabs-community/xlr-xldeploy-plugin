#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import sys

from xlr_xldeploy.XLDeployClientUtil import XLDeployClientUtil

xld_client = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)

deployment = None
deployment_package = "{0}/{1}".format(environment, deployedApplication)
print "* deployment package is {0}".format(deployment_package)
if xld_client.deployment_exists2(deployment_package):
    print "Undeploying [%s] from environment [%s] \n" % (deployment_package, environment)
    deployment = xld_client.deployment_prepare_undeploy("%s/%s" % (environment, deployedApplication), orchestrators,
                                                        deployedApplicationProperties)
else:
    if failIfApplicationDoesNotExist:
        raise Exception("No deployed application found [%s] for environment [%s]" % (deployedApplication, environment))
    else:
        print "No deployed application found [%s] for environment [%s] \n" % (deployedApplication, environment)
        sys.exit(0)

print "Creating a deployment task \n"
task_id = xld_client.get_deployment_task_id(deployment)

print "Execute task with id: %s" % task_id
task_state = xld_client.invoke_task_and_wait_for_result(task_id, pollingInterval, numberOfPollingTrials,
                                                        continueIfStepFails, numberOfContinueRetrials, failOnPause)

xld_client.display_step_logs(task_id)

if task_state in ('DONE', 'EXECUTED'):
    print "Deployment ended in %s \n" % task_state
    xld_client.archive_task(task_id)
    sys.exit(0)

# rollbackOnError
if rollbackOnError and task_state in ('FAILED', 'STOPPED'):
    print "Going to rollback \n"
    xld_client.stop_task(task_id)
    rollback_task_id = xld_client.deployment_rollback(task_id)
    task_state = xld_client.invoke_task_and_wait_for_result(rollback_task_id, pollingInterval, numberOfPollingTrials,
                                                            continueIfStepFails, numberOfContinueRetrials)
    xld_client.archive_task(rollback_task_id)
    sys.exit(1)
elif task_state in ('FAILED', 'STOPPED'):
    if cancelOnError:
        print "Task failed; cancelling task. \n"
        xld_client.cancel_task(task_id)
    else:
        print "Task failed; leaving as-is in XL Deploy. \n"
    sys.exit(1)
