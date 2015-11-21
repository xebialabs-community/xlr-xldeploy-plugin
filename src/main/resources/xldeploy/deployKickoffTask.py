#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys
import com.xhaus.jyson.JysonCodec as json
from xml.etree import ElementTree as ET
from xldeploy.XLDeployClientUtil import XLDeployClientUtil

def addNewTask(newTaskTitle, newTaskType, containerId, credentials):
  newTask={"title":newTaskTitle,"taskType":newTaskType}
  xlrResponse = XLRequest(xlrPostTasksUrl + containerId, 'POST', json.dumps(newTask), credentials['username'], credentials['password'], 'application/json').send()
  if xlrResponse.status == HTTP_SUCCESS_STATUS:
    newTask = json.loads(xlrResponse.read())
    print "New method addNewTask:  Created %s\n" % newTaskTitle
  else:
    print "New method addNewTask:  Failed to create %s\n" % newTaskTitle
    print xlrResponse.errorDump()
    sys.exit(1)  
  return newTask

def updateTask(updatedTask, credentials):
  xlrResponse = XLRequest(xlrPutTasksUrl + updatedTask['id'], 'PUT', json.dumps(updatedTask), credentials['username'], credentials['password'], 'application/json').send()
  if xlrResponse.status == HTTP_SUCCESS_STATUS:
    print "Updated Deploy polling task\n"
  else:
    print "Failed to update Deploy polling task\n"
    print xlrResponse.errorDump()
    sys.exit(1)

HTTP_SUCCESS_STATUS = 200

if xlrServer is None:
  print "No XLR server provided"
  sys.exit(1)

xldClient = XLDeployClientUtil.createXLDeployClient(xldeployServer, username, password)

deployment = None
if xldClient.deploymentExists(deploymentPackage, environment):
    print "Upgrading deployment \n"
    deployment = xldClient.deploymentPrepareUpdate(deploymentPackage,environment)
else:
    print "Creating initial deploy \n"
    deployment = xldClient.deploymentPrepareInitial(deploymentPackage, environment)

# Mapping deployables to the target environment
print "Mapping all deployables \n"
deployment = xldClient.deployment_prepare_deployeds(deployment, orchestrators, deployedApplicationProperties, deployedProperties)

preview = xldClient.deployment_preview(deployment)

# list_of_string not working on the xlrelease.deployKickoffTask.  use single rule for now; check with dev.
pauseRuleList = [pauseRule]

pauseCount = 0
previewRoot = ET.fromstring(preview) 
for metadata in previewRoot.iter('metadata'):
  for item in metadata:
    if item.tag == 'rule' and item.text in pauseRuleList:
      pauseCount = pauseCount + 1

# deploymentProperties + configure orchestrators
# print "DEBUG: Deployment description is now: %s" % deployment
# Validating the deployment
print "Creating a deployment task \n"
xldTaskId = xldClient.get_deployment_task_id(deployment)

print "Executing deployment task with id: %s\n" % xldTaskId
xldClient.invoke_task(xldTaskId)

xlrUrl = xlrServer['url']
xlrGetTasksUrl = xlrUrl.rstrip('/') + '/api/v1/tasks/'
xlrPostTasksUrl = xlrUrl.rstrip('/') + '/tasks/'
xlrPutTasksUrl = xlrUrl.rstrip('/') + '/tasks/'
credentials = CredentialsFallback(xlrServer, xlrUsername, xlrPassword).getCredentials()

currentTaskInstance = getCurrentTask()
container = '-'.join(currentTaskInstance.id.split('/')[1:-1])

xlrResponse = XLRequest(xlrGetTasksUrl + currentTaskInstance.id, 'GET', None, credentials['username'], credentials['password'], 'application/json').send()
if xlrResponse.status == HTTP_SUCCESS_STATUS:
  currentTask = json.loads(xlrResponse.read())
else:
  print "Failed to read current task\n"
  print xlrResponse.errorDump()
  sys.exit(1)

newParallelGroup = addNewTask("Deploy polling group", "xlrelease.ParallelGroup", container, credentials)
newDeployPollingTask = addNewTask("Deploy polling task", "xldeploy.DeployPollingTask", newParallelGroup['id'], credentials)

updatedDeployPollingTask = {"inputProperties":{}}
for key in newDeployPollingTask.keys():
  if key not in ('inputProperties'):
    updatedDeployPollingTask[key]	= newDeployPollingTask[key]
for key in currentTask['pythonScript'].keys():
  if key not in ('xldeployServer','xldTaskId'): 	 
    updatedDeployPollingTask['inputProperties'][key] = currentTask['pythonScript'][key]
updatedDeployPollingTask['inputProperties']['xldeployServer'] = currentTask['pythonScript']['xldeployServer'].split('/')[-1]
updatedDeployPollingTask['inputProperties']['xldTaskId'] = xldTaskId

updateTask(updatedDeployPollingTask, credentials)

print "Adding %d Pause/Continue step pairs\n" % pauseCount
for p in range(1, pauseCount + 1):
  newPauseTask = addNewTask("Pause %d" %p, "xlrelease.Task", newParallelGroup['id'], credentials)
  newScriptTask = addNewTask("Continue %d" %p, "xlrelease.ScriptTask", newParallelGroup['id'], credentials)

sys.exit(0)
