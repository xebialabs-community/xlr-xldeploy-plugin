#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys
from xldeploy.XLDeployClientUtil import XLDeployClientUtil


xldClient = XLDeployClientUtil.createXLDeployClient(xldeployServer, username, password)

packageId = xldClient.get_latest_package_version(applicationId)

if stripApplications:
    packageId = packageId.partition('/')[2]
