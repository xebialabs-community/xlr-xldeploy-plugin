#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from xldeploy.XLDeployClientUtil import XLDeployClientUtil

if not xldeployServer:
    raise Exception("XL Deploy server ID must be provided")

xld_client = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)
if xld_client.check_CI_exist(environment):
    data = xld_client.get_deployed_applications_for_environment(environment)
else:
    data = {"Invalid environment name"}
