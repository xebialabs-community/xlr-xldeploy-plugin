from xldeploy.XLDeployClient import XLDeployClient


class XLDeployClientUtil(object):

    @staticmethod
    def createXLDeployClient(container, username, password):
        client = XLDeployClient.createClient(container, username, password)
        return client