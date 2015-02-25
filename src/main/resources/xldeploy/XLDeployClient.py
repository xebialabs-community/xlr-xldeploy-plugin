import sys, time, ast
from xml.etree import ElementTree as ET
from httputil.HttpRequest import HttpRequest

class XLDeployClient(object):
    def __init__(self, httpConnection, username=None, password=None):
        self.httpRequest = HttpRequest(httpConnection, username, password)

    @staticmethod
    def createClient(httpConnection, username=None, password=None):
        return XLDeployClient(httpConnection, username, password)


    def extract_state(self, task_state_xml):
        state_pos = task_state_xml.find('state="')
        state_offset = len('state="')
        state_end_pos = task_state_xml.find('"', state_pos + state_offset + 1)
        state = task_state_xml[state_pos + state_offset:state_end_pos]
        return state


    def getParameterTypeName(self,root):
        params = root.find("parameters")
        if params:
            for child in params:
                return child.tag


    def getParameterNames(self, parameterTypeId):
        metadata_url = "/deployit/metadata/type/%s" % (parameterTypeId)
        metadata_response = self.httpRequest.get(metadata_url, contentType='application/xml')
        root = ET.fromstring(metadata_response.getResponse())
        params = root.find("property-descriptors")
        if params:
            parameterNames = []
            for child in params:
                parameterNames.append(child.get("name"))
        return parameterNames


    def addParameter(self, root, parameterTypeId, parameterName, parameters):
        params = root.find("parameters")
        propertyDict = dict(ast.literal_eval(parameters))
        if params:
            for child in params:
                if child.tag == parameterTypeId:
                    param = ET.SubElement(child, parameterName)
                    param.text = propertyDict[parameterName]


    def prepare_control_task(self, control_task_name, target_ci_id, parameters = None):
        # print 'DEBUG: prepare the control task'
        prepare_control_task_url = "/deployit/control/prepare/%s/%s" % (control_task_name, target_ci_id)
        prepare_response = self.httpRequest.get(prepare_control_task_url, contentType='application/xml')
        control_obj = prepare_response.getResponse()
        root = ET.fromstring(control_obj)
        # print 'DEBUG: Control obj from /prepare', control_obj, '\n'
        parameterTypeId = self.getParameterTypeName(root)
        # print 'DEBUG: got parameterTypeId: %s' % parameterTypeId
        if parameterTypeId:
            parameterNames = self.getParameterNames(parameterTypeId)
            # print 'Found parameter names: %s' % parameterNames
            for parameterName in parameterNames:
                self.addParameter(root, parameterTypeId, parameterName, parameters)
        # print 'DEBUG: Control obj after udating parameters ', ET.tostring(root), '\n'
        invoke_response = self.httpRequest.post('/deployit/control', ET.tostring(root), contentType='application/xml')
        task_id = invoke_response.getResponse()
        # print 'DEBUG: Control task ID', task_id, '\n'
        return task_id


    def invokeTaskAndWaitForResult(self, task_id, pollingInterval, numberOfTrials, continueIfStepFails = False, numberOfContinueRetrials = 0):
        start_task_url = "/deployit/task/%s/start" % (task_id)
        # print 'DEBUG: About to invoke task by post', task_id, '\n'
        self.httpRequest.post(start_task_url, '', contentType='application/xml')
        trial = 0
        while trial < numberOfTrials:
            # print 'DEBUG: About to get task status', task_id, '\n'
            trial += 1
            get_task_status_url = "/deployit/task/%s" % (task_id)
            task_state_response = self.httpRequest.get(get_task_status_url, contentType='application/xml')
            task_state_xml = task_state_response.getResponse()
            status = self.extract_state(task_state_xml)
            # print 'DEBUG: Task', task_id, 'now in state', status, '\n'
            if status in ('FAILED', 'STOPPED', 'CANCELLED', 'DONE', 'EXECUTED'):
                break
            time.sleep(pollingInterval)
        return status
    
    def deploymentExists(self, deploymentPackage, environment):
        deploymentExistsUrl = "/deployit/deployment/exists?application=%s&environment=%s" % (deploymentPackage.rsplit('/',1)[0],environment)
        print 'DEBUG: checking deployment exists with url %s \n' % deploymentExistsUrl
        deploymentExists_response = self.httpRequest.get(deploymentExistsUrl, contentType='application/xml')
        response = deploymentExists_response.getResponse()
        return 'true' in response
    
    def deploymentPrepareUpdate(self, deploymentPackage, environment):
        deploymentPrepareUpdateUrl = "/deployit/deployment/prepare/update?version=%s&deployedApplication=%s" % (deploymentPackage, "%s/%s" % (environment, deploymentPackage.rsplit('/',2)[1]))
        deploymentPrepareUpdate_response = self.httpRequest.get(deploymentPrepareUpdateUrl, contentType='application/xml')
        return deploymentPrepareUpdate_response.getResponse()

    def deploymentPrepareInitial(self, deploymentPackage, environment):
        deploymentPrepareInitialUrl = "/deployit/deployment/prepare/initial?version=%s&environment=%s" % (deploymentPackage, environment)
        deploymentPrepareInitial_response = self.httpRequest.get(deploymentPrepareInitialUrl, contentType='application/xml')
        return deploymentPrepareInitial_response.getResponse()
    
    def deploymentPrepareDeployeds(self, deployment):
        deploymentPrepareDeployeds = "/deployit/deployment/prepare/deployeds"
        print 'DEBUG: Prepare deployeds for deployment object %s \n' % deployment
        deploymentPrepareDeployeds_response = self.httpRequest.post(deploymentPrepareDeployeds, deployment, contentType='application/xml')
        print 'DEBUG: Deployment object including mapping is now %s \n' % deployment
        return deploymentPrepareDeployeds_response.getResponse()
    
    def getDeploymentTaskId(self, deployment):
        getDeploymentTaskId = "/deployit/deployment"
        print 'DEBUG: creating task id for deployment object %s \n' % deployment
        deploymentTaskId_response = self.httpRequest.post(getDeploymentTaskId, deployment, contentType='application/xml')
        print 'DEBUG: getDeploymentTaskId response is %s \n' % (deploymentTaskId_response.getResponse())
        return deploymentTaskId_response.getResponse()
    
    def deploymentRollback(self, taskId):
        deploymentRollback = "/deployment/rollback/%s" % taskId
        deploymentRollback_response = self.httpRequest.post(deploymentRollback,'',contentType='application/xml')
        return deploymentRollback_response.getResponse()
    
    def archiveTask(self, taskId):
        archiveTask = "/deployit/task/%s/archive" % taskId
        self.httpRequest.post(archiveTask,'',contentType='application/xml')

    def cancelTask(self, taskId):
        cancelTask = "/deployit/task/%s" % taskId
        self.httpRequest.delete(cancelTask, contentType='application/xml')