#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import re
from xlr_xldeploy.XLDeployClientUtil import XLDeployClientUtil
from xml.etree import ElementTree as ET

class DeleteInfrastructure(object):
    def __init__(self,  xldeployServer, username, password):
        self.xldClient = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)

    def delete(self, ci_id):
        infrastructure_list = self.xldClient.get_ci_tree(ci_id)
        environment_list = self.xldClient.get_ci_tree('Environments')
        for env in environment_list:
            env_ci = self.xldClient.get_ci(env, 'xml')
            root = ET.fromstring(env_ci)
            # Check for deployed applications
            if root.tag == 'udm.DeployedApplication':
                app = re.sub(r'.*/', '', root.get('id'))
                deployed_env = root.find('environment')
                deployed_env_ref = deployed_env.get('ref')
                # Check if anything from tree is deployed to env, undeploy if it is.
                for deployed in root.findall('deployeds'):
                    for ci in deployed.findall('ci'):
                        if ci.get('ref') in infrastructure_list:
                            print "Need to un-deploy %s from %s." % (app, deployed_env_ref)
                            self.undeploy(self.xldClient, app, deployed_env_ref)
            # Check if env references anything from tree, remove it if it does.
            for member in root.findall('members'):
                for ci in member.findall('ci'):
                    if ci.get('ref') in infrastructure_list:
                        print "Removing member : %s from Environment: %s" % (ci.get('ref'), env)
                        self.xldClient.remove_ci_from_environment(env, ci.get('ref'))
        # Last step, delete the CI
        self.xldClient.delete_ci(ci_id)

    def undeploy(self, xld_client, deployedApplication, environment):
        deployment = None
        deployment_package = "{0}/{1}".format(environment, deployedApplication)
        print "* deployment package is {0}".format(deployment_package)
        if xld_client.deployment_exists2(deployment_package):
            print "Undeploying [%s] from environment [%s] \n" % (deployment_package, environment)
            deployment = xld_client.deployment_prepare_undeploy("%s/%s" % (environment, deployedApplication), None, None)
        else:
            print "No deployed application found [%s] for environment [%s] \n" % (deployedApplication, environment)
            return
        print "Creating a deployment task \n"
        task_id = xld_client.get_deployment_task_id(deployment)
        print "Execute task with id: %s" % task_id
        xld_client.invoke_task_and_wait_for_result(task_id, 10, 24, True, 100, True)
        xld_client.display_step_logs(task_id)

delete = DeleteInfrastructure(xldeployServer, username, password)
delete.delete(ci_id)
