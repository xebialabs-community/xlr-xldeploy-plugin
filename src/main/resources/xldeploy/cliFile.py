#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import sys
from xldeploy.LocalCLI import Localcliscript

script = "%s" % ( str(script) )
cliScript = Localcliscript(cli['cliHome'], cli['xldHost'], cli['xldPort'], cli['xldContext'], cli['xldProxyHost'], cli['xldProxyPort'], cli['xldSocketTimeout'], cli['xldUserName'], cli['xldPassword'], script, cli['cliExecutable'], options)
exitCode = cliScript.executeFile()

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
