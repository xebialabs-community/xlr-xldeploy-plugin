#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys
import com.xhaus.jyson.JysonCodec as json
from xldeploy.XLDeployClientUtil import XLDeployClientUtil

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

newParallelGroup = {"title":"Deploy polling group","taskType":"xlrelease.ParallelGroup"}
xlrResponse = XLRequest(xlrPostTasksUrl + container, 'POST', json.dumps(newParallelGroup), credentials['username'], credentials['password'], 'application/json').send()
if xlrResponse.status == HTTP_SUCCESS_STATUS:
  newParallelGroup = json.loads(xlrResponse.read())
  print "Created Deploy polling group\n"
else:
  print "Failed to create Deploy polling group\n"
  print xlrResponse.errorDump()
  sys.exit(1)

newDeployPollingTask = {"title":"Deploy polling task","taskType":"xldeploy.DeployPollingTask"}
xlrResponse = XLRequest(xlrPostTasksUrl + newParallelGroup['id'], 'POST', json.dumps(newDeployPollingTask), credentials['username'], credentials['password'], 'application/json').send()
if xlrResponse.status == HTTP_SUCCESS_STATUS:
  newDeployPollingTask = json.loads(xlrResponse.read())
  print "Created Deploy polling task\n"
  print "DEBUG:  " + newDeployPollingTask['id'] + '\n'
else:
  print "Failed to create Deploy polling task\n"
  print xlrResponse.errorDump()
  sys.exit(1)

updatedDeployPollingTask = {"inputProperties":{}}
for key in newDeployPollingTask.keys():
  if key not in ('inputProperties'):
    updatedDeployPollingTask[key]	= newDeployPollingTask[key]
for key in currentTask['pythonScript'].keys():
  if key not in ('xldeployServer','xldTaskId'): 	 
    updatedDeployPollingTask['inputProperties'][key] = currentTask['pythonScript'][key]
updatedDeployPollingTask['inputProperties']['xldeployServer'] = currentTask['pythonScript']['xldeployServer'].split('/')[-1]
updatedDeployPollingTask['inputProperties']['xldTaskId'] = xldTaskId

xlrResponse = XLRequest(xlrPutTasksUrl + updatedDeployPollingTask['id'], 'PUT', json.dumps(updatedDeployPollingTask), credentials['username'], credentials['password'], 'application/json').send()
if xlrResponse.status == HTTP_SUCCESS_STATUS:
  print "Updated Deploy polling task\n"
else:
  print "Failed to update Deploy polling task\n"
  print xlrResponse.errorDump()
  sys.exit(1)

sys.exit(0)
