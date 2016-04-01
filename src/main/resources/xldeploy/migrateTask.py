#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from xldeploy.XLDeployClientUtil import XLDeployClientUtil

def createPath(path):
    parent = path.rpartition('/')[0]
    if not xldDestinationClient.check_CI_exist(parent):
        createPath(parent)
    xldDestinationClient.create_directory(path)

xldSourceClient = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)
xldDestinationClient = XLDeployClientUtil.create_xldeploy_client(destinationXLDeployServer, destinationUsername, destinationPassword)

if autoCreatePath:
    appPath = deploymentPackage.rpartition('/')[0]
    if not xldDestinationClient.check_CI_exist(appPath):
        parent = appPath.rpartition('/')[0]
        if not xldDestinationClient.check_CI_exist(parent):
            createPath(parent)
        xldDestinationClient.create_application(appPath)

packageUUID = xldSourceClient.get_download_uuid(deploymentPackage)
fetchURL = xldeployServer['url'] + '/deployit/internal/download/' + packageUUID
print(fetchURL)
xldDestinationClient.fetch_package(fetchURL)


