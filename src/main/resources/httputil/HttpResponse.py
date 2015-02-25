#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

class HttpResponse:
    def getStatus(self):
        """
        Gets the status code
        :return: the http status code
        """
        return self.status

    def getResponse(self):
        """
        Gets the response content
        :return: the reponse as text
        """
        return self.response

    def isSuccessful(self):
        """
        Checks if request successful
        :return: true if successful, false otherwise
        """
        return 200 <= self.status < 400

    def getHeaders(self):
        """
        Returns the response headers
        :return: a dictionary of all response headers
        """
        return self.headers

    def errorDump(self):
        """
        Dumps the whole response
        """
        print 'Status: ', self.status, '\n'
        print 'Response: ', self.response, '\n'
        print 'Response headers: ', self.headers, '\n'

    def __init__(self, status, response, headers):
        self.status = status
        self.response = response
        self.headers = {}
        for header in headers:
            self.headers[str(header.getName())] = str(header.getValue())
