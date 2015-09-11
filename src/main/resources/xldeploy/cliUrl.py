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

class localCliScript():

   def __init__(self, cliHome, xldHost, xldPort, xldContext, xldProxyHost, xldProxyPort, xldSocketTimeout, xldUserName, xldPassword, script, cliExecutable):
      self.cmdLine = CmdLine()
      self.osname = System.getProperty('os.name').lower()
      if ( self.osname.startswith('win') ):
         cliExecutable = "%s\\bin\\%s.cmd" % ( cliHome, cliExecutable )
      else:
         cliExecutable = "%s/bin/%s.sh" % ( cliHome, cliExecutable )
      # End if
      self.cmdLine.addArgument( cliExecutable )
      self.cmdLine.addArgument( '-quiet' )
      if ( xldHost != "DEFAULT" ): 
         self.cmdLine.addArgument( '-Host' )
         self.cmdLine.addArgument( xldHost )
      if ( xldPort != "DEFAULT" ):
         self.cmdLine.addArgument( '-Port' )
         self.cmdLine.addArgument( xldPort )
      if ( xldContext != "DEFAULT" ):
         self.cmdLine.addArgument( '-Context' )
         self.cmdLine.addArgument( xldContext )
      if ( xldProxyHost != "DEFAULT" ):
         self.cmdLine.addArgument( '-ProxyHost' )
         self.cmdLine.addArgument( xldProxyHost )
      if ( xldProxyPort != "DEFAULT" ):
         self.cmdLine.addArgument( '-ProxyPort' )
         self.cmdLine.addArgument( xldProxyPort )
      if ( xldSocketTimeout != "DEFAULT" ):
         self.cmdLine.addArgument( '-SocketTimeout' )
         self.cmdLine.addArgument( xldSocketTimeout )
      if ( xldUserName != "DEFAULT" ):
         self.cmdLine.addArgument( '-username' )
         self.cmdLine.addArgument( xldUserName )
      if ( xldPassword != "DEFAULT" ):
         self.cmdLine.addArgument( '-password' )
         self.cmdLine.addPassword( xldPassword )
      #
      self.script = script
      self.stdout = CapturingOverthereExecutionOutputHandler.capturingHandler()
      self.stderr = CapturingOverthereExecutionOutputHandler.capturingHandler()

   # End __init__

   def execute( self ):
      connection = None
      try:
         connection = LocalConnection.getLocalConnection()
         scriptFile = connection.getTempFile('xlrScript', '.py')
         OverthereUtils.write( String( self.script ).getBytes(), scriptFile )
         scriptFile.setExecutable(True)
         self.cmdLine.addArgument( '-source' )
         self.cmdLine.addArgument( scriptFile.getPath() )
         exitCode = connection.execute( self.stdout, self.stderr, self.cmdLine )
      except Exception, e:
            stacktrace = StringWriter()
            writer = PrintWriter(stacktrace, True)
            e.printStackTrace(writer)
            self.stderr.handleLine(stacktrace.toString())
            return 1
      finally:
            if connection is not None:
                connection.close()
      return exitCode
   # End execute

   def getStdout(self):
        return self.stdout.getOutput()
   # End getStdout

   def getStdoutLines(self):
        return self.stdout.getOutputLines()
   # End getStdoutLines

   def getStderr(self):
        return self.stderr.getOutput()
   # End getStderr

   def getStderrLines(self):
        return self.stderr.getOutputLines()
   # End getStderrLines

# End Class

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

   cliScript = localCliScript(cli['cliHome'], cli['xldHost'], cli['xldPort'], cli['xldContext'], cli['xldProxyHost'], cli['xldProxyPort'], cli['xldSocketTimeout'], cli['xldUserName'], cli['xldPassword'], script, cli['cliExecutable'])
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
