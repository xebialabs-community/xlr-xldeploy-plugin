#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from xldeploy.XLDeployClientUtil import XLDeployClientUtil

xld_client = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)

try:
    response = xld_client.check_ci_exist(applicationId)
except:
	response = False

if not response:
	raise Exception(applicationId + " does not exist")

packageIds = xld_client.get_all_package_version(applicationId)
