#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from xldeploy.XLDeployClientUtil import XLDeployClientUtil


xldSourceClient = XLDeployClientUtil.createXLDeployClient(xldeployServer, username, password)
xldDestinationClient = XLDeployClientUtil.createXLDeployClient(destinationXLDeployServer, destinationUsername, destinationPassword)

packageUUID = xldSourceClient.get_download_uuid(deploymentPackage)
fetchURL = xldeployServer['url'] + '/deployit/internal/download/' + packageUUID
print(fetchURL)
xldDestinationClient.fetch_package(fetchURL)


