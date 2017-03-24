#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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

if xld_destination_client.check_ci_exist(deploymentPackage):
    if idempotent:
        xld_destination_client.delete_ci(deploymentPackage)
    else:
        raise Exception("[%s] already exists on destination server!" % deploymentPackage)

package_uuid = xld_source_client.get_download_uuid(deploymentPackage)
fetch_url = xldeployServer['url'] + '/deployit/internal/download/' + package_uuid
print(fetch_url)
xld_destination_client.fetch_package2(fetch_url, get_username(), get_password())
