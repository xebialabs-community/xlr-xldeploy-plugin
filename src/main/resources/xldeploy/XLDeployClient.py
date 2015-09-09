#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys, time, ast, re
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


    def invoke_task_and_wait_for_result(self, task_id, polling_interval = 10, number_of_trials = None, continue_if_step_fails = False, number_of_continue_retrials = 0):
        start_task_url = "/deployit/task/%s/start" % (task_id)
        print 'DEBUG: About to invoke task by post %s - continue enabled: %s - trial: %s \n' % (task_id, continue_if_step_fails, number_of_continue_retrials)
        self.httpRequest.post(start_task_url, '', contentType='application/xml')
        trial = 0
        while not number_of_trials or trial < number_of_trials:
            # print 'DEBUG: About to get task status', task_id, '\n'
            trial += 1
            get_task_status_url = "/deployit/task/%s" % (task_id)
            task_state_response = self.httpRequest.get(get_task_status_url, contentType='application/xml')
            task_state_xml = task_state_response.getResponse()
            status = self.extract_state(task_state_xml)
            print 'DEBUG: Task', task_id, 'now in state', status, '\n'
            if status in ('FAILED') and continue_if_step_fails and number_of_continue_retrials > 0:
                status = self.invoke_task_and_wait_for_result(task_id,polling_interval,number_of_trials, continue_if_step_fails, number_of_continue_retrials-1)
            if status in ('FAILED', 'CANCELLED', 'DONE', 'EXECUTED'):
                break
            time.sleep(polling_interval)
        return status
    
    def deploymentExists(self, deploymentPackage, environment):
        deploymentExistsUrl = "/deployit/deployment/exists?application=%s&environment=%s" % (deploymentPackage.rsplit('/',1)[0],environment)
        # print 'DEBUG: checking deployment exists with url %s \n' % deploymentExistsUrl
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

    def add_orchestrators(self, root, orchestrators):
        if orchestrators:
            params = root.find(".//orchestrator")
            params.clear()
            orchs = orchestrators.split(",")
            for orch in orchs:
                orchestrator = ET.SubElement(params, 'value')
                orchestrator.text = orch.strip()
    
    def set_deployed_application_properties(self, root, deployed_application_properties):
        if deployed_application_properties:
            deployeds_application_properties_dict = dict(ast.literal_eval(deployed_application_properties))
            for key in deployeds_application_properties_dict:
                pkey_xml = root.find(key)
                if not pkey_xml:
                    pkey_xml = ET.SubElement(root.find("udm.DeployedApplication"), key)
                pkey_xml.text = deployeds_application_properties_dict[key]
                
    
    def set_deployed_properties(self, root, deployed_properties):
        if deployed_properties:
            deployeds_properties_dict = dict(ast.literal_eval(deployed_properties))
            for key in deployeds_properties_dict:
                for xlr_tag_deployed in root.findall(".//deployeds/*"):
                    print 'DEBUG: deployed is %s \n' % ET.tostring(xlr_tag_deployed)
                    print 'DEBUG: xlrTag exists? %s' % xlr_tag_deployed.findtext('xlrTag')
                    print 'DEBUG: xlrTag key? %s' % key
                    if key == xlr_tag_deployed.findtext('xlrTag'):
                        deployed_properties_dict = dict(ast.literal_eval(deployeds_properties_dict[key]))
                        print 'DEBUG: deployed properties dict is %s \n' % deployed_properties_dict
                        for pkey in deployed_properties_dict:
                            pkey_xml = xlr_tag_deployed.find(pkey)
                            if not pkey_xml:
                                pkey_xml = ET.SubElement(xlr_tag_deployed, pkey)
                            pkey_xml.text = deployed_properties_dict[pkey]
                    
    
    def deployment_prepare_deployeds(self, deployment, orchestrators = None, deployed_application_properties = None, deployed_properties = None):
        deployment_prepare_deployeds = "/deployit/deployment/prepare/deployeds"
        # print 'DEBUG: Prepare deployeds for deployment object %s \n' % deployment
        deployment_prepare_deployeds_response = self.httpRequest.post(deployment_prepare_deployeds, deployment, contentType='application/xml')
        # print 'DEBUG: Deployment object including mapping is now %s \n' % deployment
        deployment_xml = deployment_prepare_deployeds_response.getResponse()
        root = ET.fromstring(deployment_xml)
        self.add_orchestrators(root, orchestrators)
        self.set_deployed_application_properties(root, deployed_application_properties)
        print 'DEBUG: Deployment object after updating orchestrators: %s \n' % ET.tostring(root)
        self.set_deployed_properties(root, deployed_properties)
        return ET.tostring(root)
    
    def get_deployment_task_id(self, deployment):
        getDeploymentTaskId = "/deployit/deployment"
        # print 'DEBUG: creating task id for deployment object %s \n' % deployment
        deploymentTaskId_response = self.httpRequest.post(getDeploymentTaskId, deployment, contentType='application/xml')
        # print 'DEBUG: getDeploymentTaskId response is %s \n' % (deploymentTaskId_response.getResponse())
        return deploymentTaskId_response.getResponse()
    
    def deploymentRollback(self, taskId):
        deploymentRollback = "/deployit/deployment/rollback/%s" % taskId
        # print 'DEBUG: calling rollback for taskId %s \n' % taskId
        deploymentRollback_response = self.httpRequest.post(deploymentRollback,'',contentType='application/xml')
        # print 'DEBUG: received rollback taskId %s \n' % deploymentRollback_response.getResponse()
        return deploymentRollback_response.getResponse()
    
    def archiveTask(self, taskId):
        archiveTask = "/deployit/task/%s/archive" % taskId
        self.httpRequest.post(archiveTask,'',contentType='application/xml')

    def cancelTask(self, taskId):
        cancelTask = "/deployit/task/%s" % taskId
        self.httpRequest.delete(cancelTask, contentType='application/xml')

    def stopTask(self, taskId):
        stopTask = "/deployit/task/%s/stop" % taskId
        self.httpRequest.post(stopTask,'',contentType='application/xml')

    def get_download_uuid(self, deploymentPackage):
        exportTask = "/deployit/export/deploymentpackage/%s" % deploymentPackage
        exportTask_response = self.httpRequest.get(exportTask, contentType='application/xml')
        return exportTask_response.getResponse()

    def fetch_package(self, fetchURL):
        fetchTask = "/deployit/package/fetch"
        self.httpRequest.post(fetchTask, fetchURL, contentType='application/xml')

    def get_latest_package_version(self, applicationId):
        queryTask = "/deployit/repository/query?parent=%s&resultsPerPage=-1" % applicationId
        queryTask_response = self.httpRequest.get(queryTask, contentType='application/xml')
        root = ET.fromstring(queryTask_response.getResponse())
        items = root.findall('ci')
        latestPackage = ''
        latestVersion = 0
        for item in items:
            currNos = re.findall(r'\d+',item.attrib['ref'])
            if len(currNos) > 0:
                if int(currNos[0]) > latestVersion:
                    latestVersion = int(currNos[0])
                    latestPackage = item.attrib['ref']

        return latestPackage

    def check_CI_exist(self, ciId):
        queryTask = "/deployit/repository/exists/%s" % ciId
        queryTask_response = self.httpRequest.get(queryTask, contentType='application/xml')
        return queryTask_response.getResponse().find('true') > 0

    def create_directory(self, ciId):
        createTask = "/deployit/repository/ci/%s" % ciId
        xml = '<core.Directory id="' + ciId + '" />'
        self.httpRequest.post(createTask, xml, contentType='application/xml')

    def create_application(self, appId):
        createTask = "/deployit/repository/ci/%s" % appId
        xml = '<udm.Application id="' + appId + '" />'
        self.httpRequest.post(createTask, xml, contentType='application/xml')

