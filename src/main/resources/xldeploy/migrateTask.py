#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from xldeploy.XLDeployClientUtil import XLDeployClientUtil

def create_path(path):
    parent = path.rpartition('/')[0]
    if parent and not xld_destination_client.check_ci_exist(parent):
        create_path(parent)
    xld_destination_client.create_directory(path)

def get_username():
    if username:
        return username
    return xldeployServer['username']

def get_password():
    if username:
        return password
    return xldeployServer['password']

xld_source_client = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)
xld_destination_client = XLDeployClientUtil.create_xldeploy_client(destinationXLDeployServer, destinationUsername, destinationPassword)

if autoCreatePath:
    app_path = deploymentPackage.rpartition('/')[0]
    if not xld_destination_client.check_ci_exist(app_path):
        parent = app_path.rpartition('/')[0]
        if not xld_destination_client.check_ci_exist(parent):
            create_path(parent)
        xld_destination_client.create_application(app_path)

package_uuid = xld_source_client.get_download_uuid(deploymentPackage)
fetch_url = xldeployServer['url'] + '/deployit/internal/download/' + package_uuid
print(fetch_url)
xld_destination_client.fetch_package2(fetch_url, get_username(), get_password())


