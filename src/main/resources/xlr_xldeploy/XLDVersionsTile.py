#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from xlr_xldeploy.XLDeployClientUtil import XLDeployClientUtil

import org.joda.time.DateTime
import org.joda.time.format.DateTimeFormat

if not xldeployServer:
    raise Exception("XL Deploy server ID must be provided")

#check the range of values for numberOfDays,
if not 1 <= numberOfDays <= maxDays:
    numberOfDays = maxDays

xld_client = XLDeployClientUtil.create_xldeploy_client(xldeployServer, username, password)
if xld_client.check_ci_exist(environment):
    if date:
        #if date provided, set a begin_date based on provided date - number of days
        date_obj = org.joda.time.DateTime.parse(date, org.joda.time.format.DateTimeFormat.forPattern("yyyy-MM-dd"))
        begin_date = date_obj.minusDays(numberOfDays)
        begin_date = begin_date.toString("yyyy-MM-dd")
        data = xld_client.get_deployed_applications_for_environment(environment, begin_date, date)
    else:
        #set the begin_date equal to today's date - number of days
        today = org.joda.time.DateTime()
        begin_date = today.minusDays(numberOfDays)
        begin_date = begin_date.toString("yyyy-MM-dd")
        data = xld_client.get_deployed_applications_for_environment(environment, begin_date)
else:
    data = {"Invalid environment name"}
