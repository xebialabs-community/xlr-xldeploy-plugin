#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import sys
import java.lang.System as System
import httplib
import re

from java.lang import Exception
from java.io import PrintWriter
from java.io import StringWriter

from com.xebialabs.overthere import CmdLine, ConnectionOptions, OperatingSystemFamily, Overthere
from com.xebialabs.overthere.util import CapturingOverthereExecutionOutputHandler, OverthereUtils
from com.xebialabs.overthere.local import LocalConnection, LocalFile, LocalProcess
from xldeploy.LocalCLI import localCliScript

print "Script URL = %s" % ( scriptUrl )
host=scriptUrl.split('//')[1].split('/')[0]
print "Host       = %s" % ( host )
regex='^.*%s' % ( host )
uri=re.sub( regex, '', scriptUrl )
print "URI        = %s" % ( uri )
try:
   if ( scriptUrl.startswith('https') ):
       print "Make HTTPS connection"
       URLSource = httplib.HTTPSConnection( host )
   else:
       print "Make HTTP connection"
       URLSource = httplib.HTTPConnection( host )
   # End if
   URLSource.request('GET', uri, {}, {})
   response = URLSource.getresponse()
   print response.status, response.reason
   script = response.read()

   cliScript = localCliScript(cli['cliHome'], cli['xldHost'], cli['xldPort'], cli['xldContext'], cli['xldProxyHost'], cli['xldProxyPort'], cli['xldSocketTimeout'], cli['xldUserName'], cli['xldPassword'], script, cli['cliExecutable'], options)
   exitCode = cliScript.execute()

   output = cliScript.getStdout()
   err = cliScript.getStderr()
except Exception, e:
      stacktrace = StringWriter()
      writer = PrintWriter(stacktrace, True)
      e.printStackTrace(writer)
      err = stacktrace.toString()
      exitCode = 1
finally:
      URLSource.close()
# End try

if (exitCode == 0 ):
   print output
else:
   print
   print "### Exit code "
   print exitCode
   print
   print "### Output:"
   print output
   
   print "### Error stream:"
   print err
   print 
   print "----"

sys.exit(exitCode)
