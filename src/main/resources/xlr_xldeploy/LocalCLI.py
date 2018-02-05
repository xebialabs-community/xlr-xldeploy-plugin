#
# Copyright 2018 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import java.lang.System as System
import java.lang.String as String

from java.lang import Exception
from java.io import PrintWriter
from java.io import StringWriter

from com.xebialabs.overthere import CmdLine, ConnectionOptions, OperatingSystemFamily
from com.xebialabs.overthere.util import CapturingOverthereExecutionOutputHandler, OverthereUtils
from com.xebialabs.overthere.local import LocalConnection, LocalFile

class Localcliscript():

   def __init__(self, cliHome, xldHost, xldPort, xldSecure, xldContext, xldProxyHost, xldProxyPort, xldSocketTimeout, xldUserName, xldPassword, script, cliExecutable, options):
      self.cmdLine = CmdLine()
      self.osname = System.getProperty('os.name').lower()
      if self.osname.startswith('win'):
         cliExecutable = "%s\\bin\\%s.cmd" % ( cliHome, cliExecutable )
      else:
         cliExecutable = "%s/bin/%s.sh" % ( cliHome, cliExecutable )
      # End if
      self.cmdLine.addArgument( cliExecutable )
      self.cmdLine.addArgument( '-quiet' )
      if xldHost != "DEFAULT":
         self.cmdLine.addArgument( '-host' )
         self.cmdLine.addArgument( xldHost )
      if xldPort != "DEFAULT":
         self.cmdLine.addArgument( '-port' )
         self.cmdLine.addArgument( xldPort )
      if xldSecure:
          self.cmdLine.addArgument( '-secure' )
      if xldContext != "DEFAULT":
         self.cmdLine.addArgument( '-context' )
         self.cmdLine.addArgument( xldContext )
      if xldProxyHost != "DEFAULT":
         self.cmdLine.addArgument( '-proxyHost' )
         self.cmdLine.addArgument( xldProxyHost )
      if xldProxyPort != "DEFAULT":
         self.cmdLine.addArgument( '-proxyPort' )
         self.cmdLine.addArgument( xldProxyPort )
      if xldSocketTimeout != "DEFAULT":
         self.cmdLine.addArgument( '-socketTimeout' )
         self.cmdLine.addArgument( xldSocketTimeout )
      if xldUserName != "DEFAULT":
         self.cmdLine.addArgument( '-username' )
         self.cmdLine.addArgument( xldUserName )
      if xldPassword != "DEFAULT":
         self.cmdLine.addArgument( '-password' )
         self.cmdLine.addPassword( xldPassword )
      if options is not None:
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
         if len(self.options) > 1:
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

