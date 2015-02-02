# Preface #

This document describes the functionality provided by the xlr-xldeploy-plugin.

See the **XL Release Reference Manual** for background information on XL Release and release concepts.

# Overview #

The xlr-xldeploy-plugin is a XL Release plugin that allows to start a control task on XL Deploy.

## Installation ##

Place the latest released version under the `plugins` dir. If needed append the following to the `script.policy` under `conf`:

`permission java.io.FilePermission "conf/logback.xml", "read";
 permission java.lang.RuntimePermission "accessDeclaredMembers";`

## Types ##

+ ControlTask (compatible with XL Deploy 4.5.2 and up)
  * `testSpecificationName`
  * `properties`