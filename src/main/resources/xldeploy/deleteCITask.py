#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys
from xldeploy.XLDeployClientUtil import XLDeployClientUtil

xldClient = XLDeployClientUtil.createXLDeployClient(xldeployServer, username, password)

if envID:
	xldClient.removeCIFromEnvironment(envID,ciID)

xldClient.deleteCI(ciID)
