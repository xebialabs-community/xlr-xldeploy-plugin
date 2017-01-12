#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from xldeploy.XLDeployClientUtil import XLDeployClientUtil

xld_client = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)

response = False
try:
    response = xld_client.check_ci_exist(ciID)
except:
    response = False

exists = response

if throwOnFail and not response:
    raise Exception("The requested CI does not exist")