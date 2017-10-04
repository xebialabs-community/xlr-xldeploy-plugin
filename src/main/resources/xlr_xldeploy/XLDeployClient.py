#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import ast
import json
import time
from xlrelease.HttpRequest import HttpRequest
from xml.etree import ElementTree as ET


def extract_state(task_state_xml):
    state_pos = task_state_xml.find('state2="')
    state_offset = len('state2="')
    state_end_pos = task_state_xml.find('"', state_pos + state_offset + 1)
    state = task_state_xml[state_pos + state_offset:state_end_pos]
    return state


def get_parameter_type_name(root):
    params = root.find("parameters")
    if params:
        for child in params:
            return child.tag


def add_parameter(root, parameter_type_id, parameter_name, parameters):
    params = root.find("parameters")
    if params and parameters:
        property_dict = dict(ast.literal_eval(parameters))
        for child in params:
            if child.tag == parameter_type_id:
                param = ET.SubElement(child, parameter_name)
                param.text = str(property_dict[parameter_name])


def set_deployed_application_properties(deployment_xml, deployed_application_properties):
    root = ET.fromstring(deployment_xml)
    if deployed_application_properties:
        deployeds_application_properties_dict = dict(ast.literal_eval(deployed_application_properties))
        for key in deployeds_application_properties_dict:
            pkey_xml = root.find(key)
            if not pkey_xml:
                application = root.find("application")
                for child in application:
                    pkey_xml = ET.SubElement(child, key)
            pkey_xml.text = deployeds_application_properties_dict[key]
    return ET.tostring(root)


# deployed_properties must be a string, as the map_string_string type has a bug when putting the '=' in the key.
def override_deployed_properties(deployment_xml, deployed_properties):
    root = ET.fromstring(deployment_xml)
    if deployed_properties:
        deployeds_properties_dict = dict(ast.literal_eval(deployed_properties))
        for key in deployeds_properties_dict:
            for pkey_xml in root.findall(key):
                pkey_xml.text = deployeds_properties_dict[key]
    return ET.tostring(root)


# Deprecated, should be removed starting version 3.0.0
def set_deployed_properties(deployment_xml, deployed_properties):
    root = ET.fromstring(deployment_xml)
    if deployed_properties:
        deployeds_properties_dict = dict(ast.literal_eval(deployed_properties))
        for key in deployeds_properties_dict:
            for xlr_tag_deployed in root.findall(".//deployeds/*"):
                if key == xlr_tag_deployed.findtext('xlrTag'):
                    deployed_properties_dict = dict(ast.literal_eval(deployeds_properties_dict[key]))
                    for pkey in deployed_properties_dict:
                        pkey_xml = xlr_tag_deployed.find(pkey)
                        if not pkey_xml:
                            pkey_xml = ET.SubElement(xlr_tag_deployed, pkey)
                        pkey_xml.text = deployed_properties_dict[pkey]
    return ET.tostring(root)


def get_row_data(task):
    row_map = {"id": task["id"], "application": task["metadata"]["application"],
               "version": task["metadata"]["version"], "owner": task["owner"], "date": task["completionDate"]}
    return row_map


def add_orchestrators(deployment_xml, orchestrators):
    root = ET.fromstring(deployment_xml)
    if orchestrators:
        params = root.find(".//orchestrator")
        params.clear()
        orchs = orchestrators.split(",")
        for orch in orchs:
            orchestrator = ET.SubElement(params, 'value')
            orchestrator.text = orch.strip()
    return ET.tostring(root)


def check_response(response, message):
    if not response.isSuccessful():
        raise Exception(message)


class XLDeployClient(object):
    def __init__(self, http_connection, username=None, password=None):
        self.http_request = HttpRequest(http_connection, username, password)

    @staticmethod
    def create_client(http_connection, username=None, password=None):
        return XLDeployClient(http_connection, username, password)

    def get_parameter_names(self, parameter_type_id):
        metadata_url = "/deployit/metadata/type/%s" % (parameter_type_id)
        metadata_response = self.http_request.get(metadata_url, contentType='application/xml')
        root = ET.fromstring(metadata_response.getResponse())
        params = root.find("property-descriptors")
        parameter_names = []
        if params:
            for child in params:
                parameter_names.append(child.get("name"))
        return parameter_names

    def prepare_control_task(self, control_task_name, target_ci_id, parameters=None):
        prepare_control_task_url = "/deployit/control/prepare/%s/%s" % (control_task_name, target_ci_id)
        prepare_response = self.http_request.get(prepare_control_task_url, contentType='application/xml')
        check_response(prepare_response,
                       "Failed to prepare control task [%s]. Server return [%s], with content [%s]" % (
                           target_ci_id, prepare_response.status, prepare_response.response))
        control_obj = prepare_response.getResponse()
        root = ET.fromstring(control_obj)
        if parameters:
            parameter_type_id = get_parameter_type_name(root)
            if parameter_type_id:
                parameter_names = self.get_parameter_names(parameter_type_id)
                for parameterName in parameter_names:
                    add_parameter(root, parameter_type_id, parameterName, parameters)
        invoke_response = self.http_request.post('/deployit/control', ET.tostring(root), contentType='application/xml')
        check_response(invoke_response, "Failed to create control task [%s]. Server return [%s], with content [%s]" % (
            target_ci_id, invoke_response.status, invoke_response.response))
        task_id = invoke_response.getResponse()
        return task_id

    def invoke_task_and_wait_for_result(self, task_id, polling_interval=10, number_of_trials=None,
                                        continue_if_step_fails=False, number_of_continue_retrials=0,
                                        fail_on_pause=True):
        start_task_url = "/deployit/task/%s/start" % task_id
        self.http_request.post(start_task_url, '', contentType='application/xml')
        trial = 0
        while not number_of_trials or trial < number_of_trials:
            trial += 1
            get_task_status_url = "/deployit/task/%s" % task_id
            task_state_response = self.http_request.get(get_task_status_url, contentType='application/xml')
            check_response(task_state_response, "Failure to get task status")
            task_state_xml = task_state_response.getResponse()
            status = extract_state(task_state_xml)

            print 'Task [%s] now in state [%s] \n' % (task_id, status)
            if fail_on_pause:
                if status in (
                    'FAILED', 'ABORTED', 'STOPPED') and continue_if_step_fails and number_of_continue_retrials > 0:
                    status = self.invoke_task_and_wait_for_result(task_id, polling_interval, number_of_trials,
                                                                  continue_if_step_fails,
                                                                  number_of_continue_retrials - 1)
                if status in ('FAILED', 'ABORTED', 'STOPPED', 'CANCELLED', 'DONE', 'EXECUTED'):
                    break
            else:
                if status in ('FAILED', 'ABORTED') and continue_if_step_fails and number_of_continue_retrials > 0:
                    status = self.invoke_task_and_wait_for_result(task_id, polling_interval, number_of_trials,
                                                                  continue_if_step_fails,
                                                                  number_of_continue_retrials - 1)
                if status in ('FAILED', 'ABORTED', 'CANCELLED', 'DONE', 'EXECUTED'):
                    break
            time.sleep(polling_interval)
        return status

    def get_deployment_package(self, deployed_application_id):
        ci = self.get_ci(deployed_application_id, 'json')
        data = json.loads(ci)
        return data['version']

    def deployment_exists(self, deployment_package, environment):
        deployment_exists_url = "/deployit/deployment/exists?application=%s&environment=%s" % (
            deployment_package.rsplit('/', 1)[0], environment)
        deployment_exists_response = self.http_request.get(deployment_exists_url, contentType='application/xml')
        response = deployment_exists_response.getResponse()
        return 'true' in response

    def deployment_exists2(self, deployed_application):
        deployment_exists_url = "/deployit/repository/exists/{0}".format(deployed_application)
        deployment_exists_response = self.http_request.get(deployment_exists_url, contentType='application/xml')
        response = deployment_exists_response.getResponse()
        return 'true' in response

    def deployment_prepare_undeploy(self, deployed_application_id, orchestrators=None,
                                    deployed_application_properties=None):
        deployment_prepare_undeploy_url = "/deployit/deployment/prepare/undeploy?deployedApplication=%s" % deployed_application_id
        deployment_prepare_undeploy_url_response = self.http_request.get(deployment_prepare_undeploy_url,
                                                                         contentType='application/xml')
        check_response(deployment_prepare_undeploy_url_response,
                       "Failed to prepare undeploy. Server return [%s], with content [%s]" % (
                           deployment_prepare_undeploy_url_response.status,
                           deployment_prepare_undeploy_url_response.response))
        undeployment_xml = deployment_prepare_undeploy_url_response.getResponse()
        undeployment_xml = add_orchestrators(undeployment_xml, orchestrators)
        undeployment_xml = set_deployed_application_properties(undeployment_xml, deployed_application_properties)
        return undeployment_xml

    def deployment_prepare_update(self, deployment_package, environment):
        deployment_prepare_update_url = "/deployit/deployment/prepare/update?version=%s&deployedApplication=%s" % (
            deployment_package, "%s/%s" % (environment, deployment_package.rsplit('/', 2)[1]))
        deployment_prepare_update_response = self.http_request.get(deployment_prepare_update_url,
                                                                   contentType='application/xml')
        check_response(deployment_prepare_update_response,
                       "Failed to prepare update deploy. Server return [%s], with content [%s]" % (
                           deployment_prepare_update_response.status, deployment_prepare_update_response.response))
        return deployment_prepare_update_response.getResponse()

    def deployment_prepare_initial(self, deployment_package, environment):
        deployment_prepare_initial_url = "/deployit/deployment/prepare/initial?version=%s&environment=%s" % (
            deployment_package, environment)
        deployment_prepare_initial_response = self.http_request.get(deployment_prepare_initial_url,
                                                                    contentType='application/xml')
        check_response(deployment_prepare_initial_response,
                       "Failed to prepare initial deploy. Server return [%s], with content [%s]" % (
                           deployment_prepare_initial_response.status, deployment_prepare_initial_response.response))
        return deployment_prepare_initial_response.getResponse()

    def deployment_prepare_deployeds(self, deployment, orchestrators=None, deployed_application_properties=None,
                                     overrideDeployedProps=None, deployed_properties=None):
        deployment_prepare_deployeds = "/deployit/deployment/prepare/deployeds"
        deployment_prepare_deployeds_response = self.http_request.post(deployment_prepare_deployeds, deployment,
                                                                       contentType='application/xml')
        check_response(deployment_prepare_deployeds_response,
                       "Failed to prepare deployeds. Server return [%s], with content [%s]" % (
                           deployment_prepare_deployeds_response.status,
                           deployment_prepare_deployeds_response.response))
        deployment_xml = deployment_prepare_deployeds_response.getResponse()
        deployment_xml = add_orchestrators(deployment_xml, orchestrators)
        deployment_xml = set_deployed_application_properties(deployment_xml, deployed_application_properties)
        deployment_xml = override_deployed_properties(deployment_xml, overrideDeployedProps)
        deployment_xml = set_deployed_properties(deployment_xml,
                                                 deployed_properties)  # Deprecated. Should be remove starting 3.0.0
        return deployment_xml

    def validate(self, deployment):
        get_deployment_task_id = "/deployit/deployment/validate"
        deployment_with_validation_response = self.http_request.post(get_deployment_task_id, deployment,
                                                                     contentType='application/xml')
        deployment = deployment_with_validation_response.getResponse()
        root = ET.fromstring(deployment)
        return map(lambda vm: "CI: %s Message: %s" % (vm.attrib['ci'], vm.text), root.iter('validation-message'))

    def get_deployment_task_id(self, deployment):
        get_deployment_task_id = "/deployit/deployment"
        deployment_task_id_response = self.http_request.post(get_deployment_task_id, deployment,
                                                             contentType='application/xml')
        return deployment_task_id_response.getResponse()

    def deployment_rollback(self, taskId):
        deployment_rollback = "/deployit/deployment/rollback/%s" % taskId
        deployment_rollback_response = self.http_request.post(deployment_rollback, '', contentType='application/xml')
        return deployment_rollback_response.getResponse()

    def archive_task(self, task_id):
        archive_task = "/deployit/task/%s/archive" % task_id
        self.http_request.post(archive_task, '', contentType='application/xml')

    def cancel_task(self, task_id):
        cancel_task = "/deployit/task/%s" % task_id
        self.http_request.delete(cancel_task, contentType='application/xml')

    def stop_task(self, task_id):
        stop_task = "/deployit/task/%s/stop" % task_id
        self.http_request.post(stop_task, '', contentType='application/xml')

    def get_download_uuid(self, deployment_package):
        export_task = "/deployit/export/deploymentpackage/%s" % deployment_package
        export_task_response = self.http_request.get(export_task, contentType='application/xml')
        return export_task_response.getResponse()

    def fetch_package2(self, url, user_name, password):
        fetch_task = "/deployit/package/fetch2"
        params = {
            "url": url,
            "user": user_name,
            "password": password
        }
        response = self.http_request.post(fetch_task, json.dumps(params), contentType='application/json')
        check_response(response, "Failed to import package. Server return [%s], with content [%s]" % (
            response.status, response.response))

    def get_latest_package_version(self, application_id):
        query_task = "/deployit/repository/query?parent=%s&resultsPerPage=-1" % application_id
        query_task_response = self.http_request.get(query_task, contentType='application/xml')
        root = ET.fromstring(query_task_response.getResponse())
        items = root.findall('ci')
        latest_package = ''
        if len(items) > 0:
            latest_package = items[-1].attrib['ref']
        return latest_package

    def get_all_package_version(self, application_id):
        query_task = "/deployit/repository/query?parent=%s&resultsPerPage=-1" % application_id
        query_task_response = self.http_request.get(query_task, contentType='application/xml')
        root = ET.fromstring(query_task_response.getResponse())
        items = root.findall('ci')
        all_package = list()
        for item in items:
            all_package.append(item.attrib['ref'])
        return all_package

    def get_latest_deployed_version(self, environment_id, application_name):
        query_task_response = self.get_ci("%s/%s" % (environment_id, application_name), 'xml')
        root = ET.fromstring(query_task_response)
        items = root.findall('version')
        latest_package = ''
        for item in items:
            latest_package = item.attrib['ref']
        return latest_package

    def check_ci_exist(self, ci_id, throw_on_fail=False):
        query_task = "/deployit/repository/exists/%s" % ci_id
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        query_task_response = self.http_request.get(query_task, headers=headers)
        check_response(query_task_response, "Failed to check ci [%s]. Server return [%s], with content [%s]" % (
            ci_id, query_task_response.status, query_task_response.response))
        if query_task_response.getResponse().find('true') > 0:
            return True
        if throw_on_fail:
            raise Exception("CI with id [%s] does not exist or you do not have the correct permissions to read it." % ci_id)
        return False

    def create_folder_tree(self, folder_id, folder_type):
        folders = folder_id.split("/")
        folder_create = '%s' % folder_type
        for folder in folders:
            folder_create += "/" + folder
            if self.check_ci_exist(folder_create):
                print "Folder [%s] already exists" % folder_create
                print "\n"
            else:
                self.create_directory(folder_create)
                print "\n"

    def create_directory(self, ci_id):
        self.create_ci(ci_id, 'core.Directory')

    def create_application(self, app_id):
        self.create_ci(app_id, 'udm.Application')

    def create_ci(self, id, ci_type, xml_descriptor=''):
        xml = '<' + ci_type + ' id="' + id + '">' + xml_descriptor.strip() + '</' + ci_type + '>'
        create_task = '/deployit/repository/ci/%s' % id
        response = self.http_request.post(create_task, xml, contentType='application/xml')
        check_response(response, "Failed to create ci [%s]. Server return [%s], with content [%s]" % (
            id, response.status, response.response))
        print "Created ci [%s] and received response [%s]" % (id, response.response)

    def update_ci_property(self, ci_id, ci_property, property_value):
        self.check_ci_exist(ci_id, throw_on_fail=True)
        ci = self.get_ci(ci_id, 'json')
        data = json.loads(ci)
        if ci_property in data and isinstance(data[ci_property], list):
            data[ci_property] = eval(property_value)
        else:
            data[ci_property] = property_value
        self.update_ci(ci_id, json.dumps(data), 'json')

    def add_ci_to_environment(self, env_id, ci_id):
        self.check_ci_exist(env_id, throw_on_fail=True)
        ci = self.get_ci(env_id, 'json')
        data = json.loads(ci)
        data["members"].append(ci_id)
        self.update_ci(env_id, json.dumps(data), 'json')

        get_env_response = self.get_ci(env_id, 'xml')
        items = get_env_response.partition('</members>')
        xml = items[0] + '<ci ref="' + ci_id + '"/>' + items[1] + items[2]
        print(xml)
        self.update_ci(env_id, xml, 'xml')

    def remove_ci_from_environment(self, env_id, ci_id):
        get_env_response = self.get_ci(env_id, 'xml')
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
        get_ci = "/deployit/repository/ci/%s" % ci_id
        headers = {'Accept': 'application/%s' % accept, 'Content-Type': 'application/%s' % accept}
        response = self.http_request.get(get_ci, headers=headers)
        check_response(response, "Failed to get ci [%s]. Server return [%s], with content [%s]" % (
            ci_id, response.status, response.response))
        return response.getResponse()

    def update_ci(self, ci_id, data, content_type):
        update_ci = "/deployit/repository/ci/%s" % ci_id
        content_type_header = "application/%s" % content_type
        response = self.http_request.put(update_ci, data, contentType=content_type_header)
        check_response(response, "Failed to update ci [%s]. Server return [%s], with content [%s]" % (
            ci_id, response.status, response.response))

    def delete_ci(self, ci_id):
        delete_task = '/deployit/repository/ci/' + ci_id
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = self.http_request.delete(delete_task, headers=headers)
        check_response(response, "Failed to delete ci with id [%s]. Server return [%s], with content [%s]" % (
            ci_id, response.status, response.response))

    def get_ci_tree(self, ci_id):
        infrastructure_list = [ci_id]
        query = '/deployit/repository/query?parent=%s' % ci_id
        response = self.http_request.get(query, contentType='application/xml')
        check_response(response, "Unable to retrieve CI Tree from parent: %s" % ci_id)
        root = ET.fromstring(response.getResponse())
        for ci in root.findall('ci'):
            infrastructure_list.extend(self.get_ci_tree(ci.get('ref')))
        return infrastructure_list

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
                        print 'DEPLOYMENT STEP %d:  Failures=%s  State=%s\n' % (
                            step_counter, str(grandchild.attrib['failures']), str(grandchild.attrib['state']))
                        for item in grandchild:
                            if item.tag in ('description', 'startDate', 'completionDate'):
                                print '%s %s\n' % (item.tag, item.text)
                            else:
                                print "%s\n" % item.tag
                                print "%s\n" % item.text

    def query_archived_tasks(self, end_date=None):
        get_tasks = '/deployit/tasks/v2/query'
        if end_date:
            get_tasks += '?begindate=2008-01-01&enddate=%s' % end_date
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = self.http_request.get(get_tasks, headers=headers)
        check_response(response, "Failed to get archived tasks. Server return [%s], with content [%s]" % (
            response.status, response.response))
        return response.getResponse()

    def get_deployed_applications_for_environment(self, environment, date=None):
        archived_tasks = self.query_archived_tasks(date)
        deployed_apps = {}
        if archived_tasks:
            tasks = json.loads(archived_tasks)
            for task in tasks:
                if task['state'] == 'DONE' and task['metadata']['taskType'] not in (
                    'CONTROL', 'INSPECTION', 'DEFAULT') and task['metadata']['environment_id'] == environment:
                    if task['metadata']['taskType'] in ('INITIAL', 'UPGRADE', 'ROLLBACK'):
                        deployed_apps[task['metadata']['application']] = get_row_data(task)
                    if task['metadata']['taskType'] in ('UNDEPLOY') and task['metadata'][
                        'application'] in deployed_apps:
                        del deployed_apps[task['metadata']['application']]
        return deployed_apps
