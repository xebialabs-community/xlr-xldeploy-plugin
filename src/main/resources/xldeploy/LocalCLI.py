#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import java.lang.System as System
import java.lang.String as String

from java.lang import Exception
from java.io import PrintWriter
from java.io import StringWriter

from com.xebialabs.overthere import CmdLine, ConnectionOptions, OperatingSystemFamily, Overthere
from com.xebialabs.overthere.util import CapturingOverthereExecutionOutputHandler, OverthereUtils
from com.xebialabs.overthere.local import LocalConnection, LocalFile, LocalProcess

class localCliScript():

   def __init__(self, cliHome, xldHost, xldPort, xldContext, xldProxyHost, xldProxyPort, xldSocketTimeout, xldUserName, xldPassword, script, cliExecutable, options):
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
         self.cmdLine.addArgument( '-host' )
         self.cmdLine.addArgument( xldHost )
      if ( xldPort != "DEFAULT" ):
         self.cmdLine.addArgument( '-port' )
         self.cmdLine.addArgument( xldPort )
      if ( xldContext != "DEFAULT" ):
         self.cmdLine.addArgument( '-context' )
         self.cmdLine.addArgument( xldContext )
      if ( xldProxyHost != "DEFAULT" ):
         self.cmdLine.addArgument( '-proxyHost' )
         self.cmdLine.addArgument( xldProxyHost )
      if ( xldProxyPort != "DEFAULT" ):
         self.cmdLine.addArgument( '-proxyPort' )
         self.cmdLine.addArgument( xldProxyPort )
      if ( xldSocketTimeout != "DEFAULT" ):
         self.cmdLine.addArgument( '-socketTimeout' )
         self.cmdLine.addArgument( xldSocketTimeout )
      if ( xldUserName != "DEFAULT" ):
         self.cmdLine.addArgument( '-username' )
         self.cmdLine.addArgument( xldUserName )
      if ( xldPassword != "DEFAULT" ):
         self.cmdLine.addArgument( '-password' )
         self.cmdLine.addPassword( xldPassword )
      if ( options is not None ):
         self.options = str(options)
      # End if
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
         if ( len( self.options ) > 1 ):
            self.cmdLine.addArgument( '--' )
            optionsList = self.options.split(' ')
            for opt in optionsList:
                self.cmdLine.addArgument( opt )
            # End for
         # End if
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

   def executeFile( self ):
      connection = None
      try:
         connection = LocalConnection.getLocalConnection()
         scriptFile = self.script 
         print "using script %s" % ( scriptFile )
         #scriptFile.setExecutable(True)
         self.cmdLine.addArgument( '-source' )
         self.cmdLine.addArgument( scriptFile )
         if ( len( self.options ) > 1 ):
            self.cmdLine.addArgument( '--' )
            optionsList = self.options.split(' ')
            for opt in optionsList:
                self.cmdLine.addArgument( opt )
            # End for
         # End if
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

