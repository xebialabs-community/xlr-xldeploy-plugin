#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys, time

def extract_state(task_state_xml):
    state_pos = task_state_xml.find('state="')
    state_offset = len('state="')
    state_end_pos = task_state_xml.find('"', state_pos + state_offset + 1)
    state = task_state_xml[state_pos + state_offset:state_end_pos]
    return state

def prepare_control_task(xld_call_factory, control_task_name, target_ci_id):
    # prepare the control task
    prepare_control_task_url = "/control/prepare/%s/%s" % (control_task_name, target_ci_id)
    prepare_response = xld_call_factory.get(prepare_control_task_url, contentType = 'application/xml')
    control_obj = prepare_response.getResponse()
    # print 'DEBUG: Control obj from /prepare', control_obj, '\n'
    # no parameters needed, so can invoke directly
    invoke_response = xld_call_factory.post('/control', control_obj, contentType = 'application/xml')
    task_id = invoke_response.getResponse()
    print 'DEBUG: Control task ID', task_id, '\n'
    return task_id

def invoke_task_and_wait_for_result(xld_call_factory, task_id):
    start_task_url = "/task/%s/start" % (task_id)
    # print 'DEBUG: About to invoke task by post', task_id, '\n'
    xld_call_factory.post(start_task_url, '', contentType = 'application/xml')
    while True:
        # print 'DEBUG: About to get task status', task_id, '\n'
        get_task_status_url = "/task/%s" % (task_id)
        task_state_response = xld_call_factory.get(get_task_status_url, contentType = 'application/xml')
        task_state_xml = task_state_response.getResponse()
        status = extract_state(task_state_xml)
        # print 'DEBUG: Task', task_id, 'now in state', status, '\n'
        if status in ('FAILED','STOPPED','CANCELLED','DONE','EXECUTED'):
            break
        time.sleep(5)
    return status

xld_call_factory = HttpRequest({'url': xldeployServer['url']}, xldeployServer['username'], xldeployServer['password'])
# print 'DEBUG: About to prepare %s on %s\n' % (controlTaskName, ciId)
task_id = prepare_control_task(xld_call_factory, controlTaskName, ciId)
# print 'DEBUG: About to invoke task and wait for response', task_id, '\n'
task_state = invoke_task_and_wait_for_result(xld_call_factory, task_id)
# print 'DEBUG: Task state for', task_id, ':', task_state, '\n'

