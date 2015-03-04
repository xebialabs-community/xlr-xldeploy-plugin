#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys
from xldeploy.XLDeployClientUtil import XLDeployClientUtil


xldClient = XLDeployClientUtil.createXLDeployClient(xldeployServer, username, password)

print 'DEBUG: About to prepare %s on %s\n' % (controlTaskName, ciId)
task_id = xldClient.prepare_control_task(controlTaskName, ciId, parameters)
print 'DEBUG: About to invoke task and wait for response', task_id, '\n'
task_state = xldClient.invoke_task_and_wait_for_result(task_id, pollingInterval, numberOfPollingTrials, continueIfStepFails, numberOfContinueRetrials)
print 'DEBUG: Task state for', task_id, ':', task_state, '\n'
xldClient.archiveTask(task_id)
if task_state in ('DONE','EXECUTED'):
    sys.exit(0)
sys.exit(1)


