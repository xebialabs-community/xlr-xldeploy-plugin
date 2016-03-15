#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys, time, ast, re
import com.xhaus.jyson.JysonCodec as json

from xml.etree import ElementTree as ET
from xlrelease.HttpRequest import HttpRequest

class XLDeployClient(object):
    def __init__(self, httpConnection, username=None, password=None):
        self.http_request = HttpRequest(httpConnection, username, password)

    @staticmethod
    def createClient(httpConnection, username=None, password=None):
        return XLDeployClient(httpConnection, username, password)


    def extract_state(self, task_state_xml):
        state_pos = task_state_xml.find('state2="')
        state_offset = len('state2="')
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
        metadata_response = self.http_request.get(metadata_url, contentType='application/xml')
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
        prepare_response = self.http_request.get(prepare_control_task_url, contentType='application/xml')
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
        invoke_response = self.http_request.post('/deployit/control', ET.tostring(root), contentType='application/xml')
        task_id = invoke_response.getResponse()
        # print 'DEBUG: Control task ID', task_id, '\n'
        return task_id


    def invoke_task_and_wait_for_result(self, task_id, polling_interval = 10, number_of_trials = None, continue_if_step_fails = False, number_of_continue_retrials = 0, fail_on_pause = True):
        start_task_url = "/deployit/task/%s/start" % (task_id)
        # print 'DEBUG: About to invoke task by post %s - continue enabled: %s - trial: %s \n' % (task_id, continue_if_step_fails, number_of_continue_retrials)
        self.http_request.post(start_task_url, '', contentType='application/xml')
        trial = 0
        while not number_of_trials or trial < number_of_trials:
            # print 'DEBUG: About to get task status', task_id, '\n'
            trial += 1
            get_task_status_url = "/deployit/task/%s" % (task_id)
            task_state_response = self.http_request.get(get_task_status_url, contentType='application/xml')
            task_state_xml = task_state_response.getResponse()
            # print 'DEBUG task_state_xml is ' + task_state_xml
            status = self.extract_state(task_state_xml)
            print 'Task', task_id, 'now in state', status, '\n'
            if fail_on_pause:
                if status in ('FAILED', 'ABORTED', 'STOPPED') and continue_if_step_fails and number_of_continue_retrials > 0:
                    status = self.invoke_task_and_wait_for_result(task_id,polling_interval,number_of_trials, continue_if_step_fails, number_of_continue_retrials-1)
                if status in ('FAILED', 'ABORTED', 'STOPPED', 'CANCELLED', 'DONE', 'EXECUTED'):
                    break
            else:
                if status in ('FAILED', 'ABORTED') and continue_if_step_fails and number_of_continue_retrials > 0:
                    status = self.invoke_task_and_wait_for_result(task_id,polling_interval,number_of_trials, continue_if_step_fails, number_of_continue_retrials-1)
                if status in ('FAILED', 'ABORTED', 'CANCELLED', 'DONE', 'EXECUTED'):
                    break
            time.sleep(polling_interval)
        return status

    def get_deployment_package(self, deployed_application_id):
        ci = self.get_ci(deployed_application_id,'json')
        data = json.loads(ci)
        return data['version']


    def deployment_exists(self, deployment_package, environment):
        deployment_exists_url = "/deployit/deployment/exists?application=%s&environment=%s" % (deployment_package.rsplit('/',1)[0],environment)
        # print 'DEBUG: checking deployment exists with url %s \n' % deployment_exists_url
        deployment_exists_response = self.http_request.get(deployment_exists_url, contentType='application/xml')
        response = deployment_exists_response.getResponse()
        return 'true' in response

    def deployment_prepare_undeploy(self, deployed_application_id):
        deployment_prepare_undeploy_url = "/deployit/deployment/prepare/undeploy?deployedApplication=%s" % (deployed_application_id)
        deployment_prepare_undeploy_url_response = self.http_request.get(deployment_prepare_undeploy_url, contentType='application/xml')
        return deployment_prepare_undeploy_url_response.getResponse()

    def deploymentPrepareUpdate(self, deploymentPackage, environment):
        deploymentPrepareUpdateUrl = "/deployit/deployment/prepare/update?version=%s&deployedApplication=%s" % (deploymentPackage, "%s/%s" % (environment, deploymentPackage.rsplit('/',2)[1]))
        deploymentPrepareUpdate_response = self.http_request.get(deploymentPrepareUpdateUrl, contentType='application/xml')
        return deploymentPrepareUpdate_response.getResponse()

    def deploymentPrepareInitial(self, deploymentPackage, environment):
        deploymentPrepareInitialUrl = "/deployit/deployment/prepare/initial?version=%s&environment=%s" % (deploymentPackage, environment)
        deploymentPrepareInitial_response = self.http_request.get(deploymentPrepareInitialUrl, contentType='application/xml')
        return deploymentPrepareInitial_response.getResponse()

    def add_orchestrators(self, deployment_xml, orchestrators):
        root = ET.fromstring(deployment_xml)
        if orchestrators:
            params = root.find(".//orchestrator")
            params.clear()
            orchs = orchestrators.split(",")
            for orch in orchs:
                orchestrator = ET.SubElement(params, 'value')
                orchestrator.text = orch.strip()
        return ET.tostring(root)

    def set_deployed_application_properties(self, deployment_xml, deployed_application_properties):
        root = ET.fromstring(deployment_xml)
        if deployed_application_properties:
            deployeds_application_properties_dict = dict(ast.literal_eval(deployed_application_properties))
            # print 'DEBUG: deployed application properties dict is %s \n' % deployeds_application_properties_dict
            # print 'DEBUG: Deployment object is now: %s \n' % ET.tostring(root)
            for key in deployeds_application_properties_dict:
                # print "DEBUG: Key is %s" % key
                pkey_xml = root.find(key)
                if not pkey_xml:
                    application = root.find("application")
                    for child in application:
                        # print "DEBUG: Going to add key: %s" % key
                        # print "DEBUG: Searching for deployed application: %s" % child
                        pkey_xml = ET.SubElement(child, key)
                pkey_xml.text = deployeds_application_properties_dict[key]
        return ET.tostring(root)
                
    
    def set_deployed_properties(self, deployment_xml, deployed_properties):
        root = ET.fromstring(deployment_xml)
        if deployed_properties:
            deployeds_properties_dict = dict(ast.literal_eval(deployed_properties))
            for key in deployeds_properties_dict:
                for xlr_tag_deployed in root.findall(".//deployeds/*"):
                    # print 'DEBUG: deployed is %s \n' % ET.tostring(xlr_tag_deployed)
                    # print 'DEBUG: xlrTag exists? %s' % xlr_tag_deployed.findtext('xlrTag')
                    # print 'DEBUG: xlrTag key? %s' % key
                    if key == xlr_tag_deployed.findtext('xlrTag'):
                        deployed_properties_dict = dict(ast.literal_eval(deployeds_properties_dict[key]))
                        # print 'DEBUG: deployed properties dict is %s \n' % deployed_properties_dict
                        for pkey in deployed_properties_dict:
                            pkey_xml = xlr_tag_deployed.find(pkey)
                            if not pkey_xml:
                                pkey_xml = ET.SubElement(xlr_tag_deployed, pkey)
                            pkey_xml.text = deployed_properties_dict[pkey]
        return ET.tostring(root)
                    
    
    def deployment_prepare_deployeds(self, deployment, orchestrators = None, deployed_application_properties = None, deployed_properties = None):
        deployment_prepare_deployeds = "/deployit/deployment/prepare/deployeds"
        # print 'DEBUG: Prepare deployeds for deployment object %s \n' % deployment
        deployment_prepare_deployeds_response = self.http_request.post(deployment_prepare_deployeds, deployment, contentType='application/xml')
        if not deployment_prepare_deployeds_response.isSuccessful():
            raise Exception("Failed to prepare deployeds. Server return [%s], with content [%s]" % (deployment_prepare_deployeds_response.status, deployment_prepare_deployeds_response.response))
        deployment_xml = deployment_prepare_deployeds_response.getResponse()
        # print 'DEBUG: deployment_xml is ' + deployment_xml
        deployment_xml = self.add_orchestrators(deployment_xml, orchestrators)
        deployment_xml = self.set_deployed_application_properties(deployment_xml, deployed_application_properties)
        # print 'DEBUG: Deployment object after updating orchestrators: %s \n' % ET.tostring(root)
        deployment_xml = self.set_deployed_properties(deployment_xml, deployed_properties)
        return deployment_xml
    
    def get_deployment_task_id(self, deployment):
        getDeploymentTaskId = "/deployit/deployment"
        # print 'DEBUG: creating task id for deployment object %s \n' % deployment
        deploymentTaskId_response = self.http_request.post(getDeploymentTaskId, deployment, contentType='application/xml')
        # print 'DEBUG: getDeploymentTaskId response is %s \n' % (deploymentTaskId_response.getResponse())
        return deploymentTaskId_response.getResponse()
    
    def deployment_rollback(self, taskId):
        deploymentRollback = "/deployit/deployment/rollback/%s" % taskId
        # print 'DEBUG: calling rollback for taskId %s \n' % taskId
        deploymentRollback_response = self.http_request.post(deploymentRollback,'',contentType='application/xml')
        # print 'DEBUG: received rollback taskId %s \n' % deploymentRollback_response.getResponse()
        return deploymentRollback_response.getResponse()
    
    def archive_task(self, task_id):
        archive_task = "/deployit/task/%s/archive" % task_id
        self.http_request.post(archive_task,'',contentType='application/xml')

    def cancel_task(self, taskId):
        cancelTask = "/deployit/task/%s" % taskId
        self.http_request.delete(cancelTask, contentType='application/xml')

    def stop_task(self, taskId):
        stopTask = "/deployit/task/%s/stop" % taskId
        self.http_request.post(stopTask,'',contentType='application/xml')

    def get_download_uuid(self, deploymentPackage):
        exportTask = "/deployit/export/deploymentpackage/%s" % deploymentPackage
        exportTask_response = self.http_request.get(exportTask, contentType='application/xml')
        return exportTask_response.getResponse()

    def fetch_package(self, fetchURL):
        fetchTask = "/deployit/package/fetch"
        self.http_request.post(fetchTask, fetchURL, contentType='application/xml')

    def get_latest_package_version(self, application_id):
        query_task = "/deployit/repository/query?parent=%s&resultsPerPage=-1" % application_id
        query_task_response = self.http_request.get(query_task, contentType='application/xml')
        root = ET.fromstring(query_task_response.getResponse())
        items = root.findall('ci')
        latest_package = ''
        if len(items) > 0:
            latest_package = items[-1].attrib['ref']
        return latest_package

    def get_latest_deployed_version(self, environment_id, application_name):
        query_task_response = self.get_ci(self,"%s/%s" % (environment_id, application_name), 'xml')
        root = ET.fromstring(query_task_response)
        items = root.findall('version')
        latest_package = ''
        for item in items:
             latest_package = item.attrib['ref']
        # End for
        return latest_package

    def check_CI_exist(self, ci_id):
        queryTask = "/deployit/repository/exists/%s" % ci_id
        queryTask_response = self.http_request.get(queryTask, contentType='application/xml')
        return queryTask_response.getResponse().find('true') > 0

    def create_directory(self, ciId):
        createTask = "/deployit/repository/ci/%s" % ciId
        xml = '<core.Directory id="' + ciId + '" />'
        self.http_request.post(createTask, xml, contentType='application/xml')

    def create_application(self, appId):
        createTask = "/deployit/repository/ci/%s" % appId
        xml = '<udm.Application id="' + appId + '" />'
        self.http_request.post(createTask, xml, contentType='application/xml')

    def createCI(self, id, ciType, xmlDescriptor):
        xml = '<' + ciType + ' id="' + id + '">' + xmlDescriptor + '</' + ciType + '>'
        createTask = '/deployit/repository/ci/' + id
        self.http_request.post(createTask, xml, contentType='application/xml')

    def update_ci_property(self, ci_id, ci_property, property_value):
        if self.check_CI_exist(ci_id):
            ci = self.get_ci(ci_id, 'json')
            data = json.loads(ci)
            data[ci_property] = property_value
            self.update_ci(ci_id, json.dumps(data), 'json')
        else:
            raise Exception("Did not find ci with id [%s]" % ci_id)

    def add_ci_to_environment(self, env_id, ci_id):
        get_env_response = self.get_ci(self,env_id, 'xml')
        items = get_env_response.partition('</members>')
        xml = items[0] + '<ci ref="' + ci_id + '"/>' + items[1] + items[2]
        print(xml)
        self.update_ci(env_id, xml, 'xml')

    def remove_ci_from_environment(self, env_id, ci_id):
        get_env_response = self.get_ci(self,env_id, 'xml')
        print get_env_response
        env_root = ET.fromstring(get_env_response)
        member_to_remove = None
        for child in env_root:
          if child.tag == 'members':
            for member in child:
              if member.attrib['ref'] == ci_id:
                print 'Found ' + ci_id + ' in ' + env_id
                env_members = child
                member_to_remove = member
        if member_to_remove is not None:
          print 'Removing ' + ci_id + ' from ' + env_id
          env_members.remove(member_to_remove)
          self.update_ci(env_id, ET.tostring(env_root), 'xml')

    def get_ci(self, ci_id, accept):
        get_ci = "/deployit/repository/ci/%s" % (ci_id)
        headers = {'Accept': 'application/%s' % accept}
        return self.http_request.get(get_ci, headers = headers).getResponse()

    def update_ci(self, ci_id, data, content_type):
        update_ci = "/deployit/repository/ci/%s" % ci_id
        content_type_header = "application/%s" % content_type
        response = self.http_request.put(update_ci, data, contentType=content_type_header)
        if not response.isSuccessful():
            raise Exception("Failed to update ci [%s]. Server return [%s], with content [%s]" % (ci_id, response.status, response.response))

    def delete_ci(self, ci_id):
        delete_task = '/deployit/repository/ci/' + ci_id
        self.http_request.delete(delete_task)

    def display_step_logs(self, task_id):
        get_task_steps = '/deployit/task/' + task_id + '/step'
        get_task_steps_response = self.http_request.get(get_task_steps, contentType='application/xml')
        task_steps_root = ET.fromstring(get_task_steps_response.getResponse())
        for child in task_steps_root:
            if child.tag == 'steps':
                step_counter = 0
                for grandchild in child:
                    if grandchild.tag == 'step':
                        step_counter = step_counter + 1
                        print 'DEPLOYMENT STEP %d:  Failures=%s  State=%s\n' % (step_counter, str(grandchild.attrib['failures']), str(grandchild.attrib['state']))
                        for item in grandchild:
                            if item.tag in ('description', 'startDate', 'completionDate'):
                                print '%s %s\n' % (str(item.tag), str(item.text))
                            else:
                                print str(item.tag) + '\n' 
                                print str(item.text) + '\n' 
