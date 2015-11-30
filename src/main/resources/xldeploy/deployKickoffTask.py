#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys
import com.xhaus.jyson.JysonCodec as json
from xml.etree import ElementTree as ET
from xldeploy.XLDeployClientUtil import XLDeployClientUtil
# New
from xlr.XLReleaseClientUtil import XLReleaseClientUtil
#

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
pauseDescriptions = []
previewRoot = ET.fromstring(preview) 

for step in previewRoot.iter('step'):
  pauseStep = 'false'
  for child in step:
    if child.tag == 'metadata':
      for item in child:
        if item.tag == 'rule' and item.text in pauseRuleList:
          pauseStep = 'true'
  if pauseStep == 'true':
    for child in step:
      if child.tag == 'description':
        pauseDescriptions.append(child.text)

print "Creating a deployment task \n"
xldTaskId = xldClient.get_deployment_task_id(deployment)

print "Executing deployment task with id: %s\n" % xldTaskId
xldClient.invoke_task(xldTaskId)

xlrUrl = xlrServer['url']
xlrGetTasksUrl = xlrUrl.rstrip('/') + '/api/v1/tasks/'
xlrPostTasksUrl = xlrUrl.rstrip('/') + '/tasks/'
xlrPutTasksUrl = xlrUrl.rstrip('/') + '/tasks/'
xlrLinkTasksUrl = xlrUrl.rstrip('/') + '/planning/links/'

xlrClient = XLReleaseClientUtil.createXLReleaseClient(xlrServer, xlrUsername, xlrPassword)

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

newParallelGroup = xlrClient.add_new_task("Deploy polling group", "xlrelease.ParallelGroup", container)
newDeployPollingTask = xlrClient.add_new_task("Deploy polling task", "xldeploy.DeployPollingTask", newParallelGroup['id'])

updatedDeployPollingTask = {"inputProperties":{}}
for key in newDeployPollingTask.keys():
  if key not in ('inputProperties'):
    updatedDeployPollingTask[key]	= newDeployPollingTask[key]
for key in currentTask['pythonScript'].keys():
  if key not in ('xldeployServer','xldTaskId'): 	 
    updatedDeployPollingTask['inputProperties'][key] = currentTask['pythonScript'][key]
updatedDeployPollingTask['inputProperties']['xldeployServer'] = currentTask['pythonScript']['xldeployServer'].split('/')[-1]
updatedDeployPollingTask['inputProperties']['xldTaskId'] = xldTaskId

xlrClient.update_task(updatedDeployPollingTask)

print "Adding Pause/Continue step pairs\n"
for p in range(len(pauseDescriptions)):
  newPauseTask = xlrClient.add_new_task("Pause:  %s" % pauseDescriptions[p], "xlrelease.Task", newParallelGroup['id'])
  newWebhookTask = xlrClient.add_new_task("Continue:  %s" % pauseDescriptions[p], "webhook.XmlWebhook", newParallelGroup['id'])
  newWebhookTask['inputProperties']['URL'] = xldeployServer['url'] + '/deployit/task/' + xldTaskId + '/start'
  newWebhookTask['inputProperties']['method'] = 'POST'
  newWebhookTask['inputProperties']['username'] = xldeployServer['username']
  newWebhookTask['passwordProperties']['password']['password'] = xldeployServer['password']
  xlrClient.update_task(newWebhookTask)

  # To chain Pause/Continue tasks, uncomment:
  # if p > 1:
  #   print "Link previous Continue Task %d to Pause Task %d\n" % (p-1, p)
  #   xlrClient.add_link(newParallelGroup['id'], previousWebhookTaskId, newPauseTask['id'])
  
  print "Link Pause Task to Continue Task\n"
  xlrClient.add_link(newParallelGroup['id'], newPauseTask['id'], newWebhookTask['id'])
  previousWebhookTaskId = newWebhookTask['id']

sys.exit(0)
