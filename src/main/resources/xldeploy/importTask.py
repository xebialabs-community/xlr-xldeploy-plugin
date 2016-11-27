#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from xldeploy.XLDeployClientUtil import XLDeployClientUtil
import json

xldClient = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)
fetch_task = "/deployit/package/fetch2"
params = {
    "url": repositoryUrl,
    "user": repositoryUsername,
    "password": repositoryPassword
}
response = xldClient.http_request.post(fetch_task, json.dumps(params), contentType='application/json')
if not response.isSuccessful():
    raise Exception("Failed to import package. Server return [%s], with content [%s]" % (response.status, response.response))
