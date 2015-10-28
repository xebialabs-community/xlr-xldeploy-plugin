#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import sys
import java.lang.System as System

from java.lang import Exception
from java.io import PrintWriter
from java.io import StringWriter

from com.xebialabs.overthere import CmdLine, ConnectionOptions, OperatingSystemFamily, Overthere
from com.xebialabs.overthere.util import CapturingOverthereExecutionOutputHandler, OverthereUtils
from com.xebialabs.overthere.local import LocalConnection, LocalFile, LocalProcess
from xldeploy.LocalCLI import localCliScript

cliScript = localCliScript(cli['cliHome'], cli['xldHost'], cli['xldPort'], cli['xldContext'], cli['xldProxyHost'], cli['xldProxyPort'], cli['xldSocketTimeout'], cli['xldUserName'], cli['xldPassword'], script, cli['cliExecutable'], options)
exitCode = cliScript.execute()

output = cliScript.getStdout()
err = cliScript.getStderr()

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
