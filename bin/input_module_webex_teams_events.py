
# encoding = utf-8

import os
import sys
import time
import datetime
import time as mytime
import json
import urllib
from lib.get_access_token_helper import get_access_token, update_access_token

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # global_account = definition.parameters.get('global_account', None)
    pass

def collect_events(helper, ew):
    """Implement your data collection logic here

    # The following examples get the arguments of this input.
    # Note, for single instance mod input, args will be returned as a dict.
    # For multi instance mod input, args will be returned as a single value.
    opt_global_account = helper.get_arg('global_account')
    # In single instance mode, to get arguments of a particular input, use
    opt_global_account = helper.get_arg('global_account', stanza_name)

    # get input type
    helper.get_input_type()

    # The following examples get input stanzas.
    # get all detailed input stanzas
    helper.get_input_stanza()
    # get specific input stanza with stanza name
    helper.get_input_stanza(stanza_name)
    # get all stanza names
    helper.get_input_stanza_names()

    # The following examples get options from setup page configuration.
    # get the loglevel from the setup page
    loglevel = helper.get_log_level()
    # get proxy setting configuration
    proxy_settings = helper.get_proxy()
    # get account credentials as dictionary
    account = helper.get_user_credential_by_username("username")
    account = helper.get_user_credential_by_id("account id")
    # get global variable configuration
    global_client_id = helper.get_global_setting("client_id")
    global_client_secret = helper.get_global_setting("client_secret")
    global_refresh_token = helper.get_global_setting("refresh_token")

    # The following examples show usage of logging related helper functions.
    # write to the log for this modular input using configured global log level or INFO as default
    helper.log("log message")
    # write to the log using specified log level
    helper.log_debug("log message")
    helper.log_info("log message")
    helper.log_warning("log message")
    helper.log_error("log message")
    helper.log_critical("log message")
    # set the log level for this modular input
    # (log_level can be "debug", "info", "warning", "error" or "critical", case insensitive)
    helper.set_log_level(log_level)

    # The following examples send rest requests to some endpoint.
    response = helper.send_http_request(url, method, parameters=None, payload=None,
                                        headers=None, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=True)
    # get the response headers
    r_headers = response.headers
    # get the response body as text
    r_text = response.text
    # get response body as json. If the body text is not a json string, raise a ValueError
    r_json = response.json()
    # get response cookies
    r_cookies = response.cookies
    # get redirect history
    historical_responses = response.history
    # get response status code
    r_status = response.status_code
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()

    # The following examples show usage of check pointing related helper functions.
    # save checkpoint
    helper.save_check_point(key, state)
    # delete checkpoint
    helper.delete_check_point(key)
    # get checkpoint
    state = helper.get_check_point(key)

    # To create a splunk event
    helper.new_event(data, time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    """

    '''
    # The following example writes a random number as an event. (Multi Instance Mode)
    # Use this code template by default.
    import random
    data = str(random.randint(0,100))
    event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=data)
    ew.write_event(event)
    '''

    '''
    # The following example writes a random number as an event for each input config. (Single Instance Mode)
    # For advanced users, if you want to create single instance mod input, please use this code template.
    # Also, you need to uncomment use_single_instance_mode() above.
    import random
    input_type = helper.get_input_type()
    for stanza_name in helper.get_input_stanza_names():
        data = str(random.randint(0,100))
        event = helper.new_event(source=input_type, index=helper.get_output_index(stanza_name), sourcetype=helper.get_sourcetype(stanza_name), data=data)
        ew.write_event(event)
    '''

    proxy_settings = helper.get_proxy()

    index = helper.get_output_index()
    source = helper.get_input_type() + "://" + helper.get_input_stanza_names()
    sourcetype = helper.get_sourcetype()
    host = "api.ciscospark.com"
    
    resource = helper.get_arg("resource")

    client_id = helper.get_global_setting('client_id')
    client_secret = helper.get_global_setting('client_secret')
    certificate_verification = True if (helper.get_global_setting('certificate_verification') == 1) else False

    message_masking = helper.get_arg('message_masking')
    fetch_attachment_information = helper.get_arg('fetch_attachment_information')
    fetch_room_information = helper.get_arg('fetch_attachment_information')
    
    # Get access token from storage/password endpoint
    access_token = get_access_token(helper, client_id, client_secret)

    checkpoint_name = "last_run_" + client_id + "_" + helper.get_input_stanza_names()
    
    helper.log_debug("[-] EVENTS: checkpoint_name: {}".format(checkpoint_name))
    
    last_run =  helper.get_check_point(checkpoint_name)
    # # Overrride once to get old events
    # #last_run = '2020-05-16T09:34:00.000Z'

    if last_run is None:
        last_run = datetime.datetime.utcnow().isoformat()[:-3] + 'Z'
        # We need a small offset as API does not allow this to be the same
        helper.save_check_point(checkpoint_name, last_run)
        helper.log_debug("[-] EVENTS: Storing first checkpoint")
    else: 
        # shift last_run by 1 second
        last_run = (datetime.datetime.strptime(last_run, '%Y-%m-%dT%H:%M:%S.%fZ') +
                          datetime.timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    current_run = datetime.datetime.utcnow().isoformat()[:-3] + 'Z'
    helper.log_debug("[-] EVENTS: last_run: {}".format(last_run))
    helper.log_debug("[-] EVENTS: current_run: {}".format(current_run))


    # Fetching Events:
    
    #last_run ='2020-07-22T00:00:00.000Z'   
    #current_run ='2020-07-22T11:22:00.000Z'

    
    events_url = 'https://api.ciscospark.com/v1/events?resource='+resource+'&from={}&to={}'.format(last_run, current_run)
    
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Accept' : 'application/json',
        'cache-control' : 'no-cache',
        'Authorization' : 'Bearer {}'.format(access_token)
        }
    
    method = "GET"
    
    helper.log_debug("[-] EVENTS: events_url: {}".format(events_url))
    
    
    paging = True
    
    while paging == True:

        response = helper.send_http_request(events_url, method, parameters=None, payload=None, headers=headers, cookies=None, verify=certificate_verification, cert=None, timeout=None, use_proxy=True)
           
        response_dict = response.json()
    
        if response.status_code != 200:
            helper.log_error("[-] EVENTS: status_code: {}. Exiting.".format(response.status_code))
            helper.log_error("[-] EVENTS: response: {}".format(response_dict))
            sys.exit()
            
        else:
            helper.log_info("[-] EVENTS: status_code: {}.".format(response.status_code))

            response_headers = response.headers
            helper.log_debug("[-] EVENTS: response_headers: {}.".format(response_headers))
            

            for data in response_dict.get("items"):
                #helper.log_debug("data: {}".format(json.dumps(data)))
                if message_masking == True:
                    data["data"]["text"] = "***masked***"
                
                #############################
                # Fetch Attachment Information
                if fetch_attachment_information == True and data["data"].get("files") != None:
                    helper.log_debug("[-] EVENTS: Found attachment files. Fetching Headers")
                    
                    files = {}
                    for file_url in data["data"].get("files"):
                        helper.log_debug("[-] EVENTS: File URL: {}".format(file_url))
                        file_method = "HEAD"
                        file_response = helper.send_http_request(file_url, file_method, parameters=None, payload=None, headers=headers, cookies=None, verify=certificate_verification, cert=None, timeout=None, use_proxy=True)
           
                        helper.log_debug("[-] EVENTS: File response: {}".format(file_response.status_code))

                        if file_response.status_code == 200:
                            file_response_headers = file_response.headers
                            helper.log_debug("[-] EVENTS: file response_headers: {}.".format(file_response_headers))
                            content_disposition =  file_response_headers.get("Content-Disposition")
                            content_encoding =  file_response_headers.get("Content-Encoding")
                            content_length =  file_response_headers.get("Content-Length")
                            content_type =  file_response_headers.get("Content-Type")

                            files_dict = {
                                    'file_url': file_url,
                                    'content_disposition': content_disposition,
                                    'content_encoding': content_encoding,
                                    'content_length': content_length,
                                    'content_type': content_type
                            }
                            
                            files.update(files_dict)
                            
                        elif file_response.status_code == 404:
                            helper.log_error("[-] EVENTS: file status_code: {}. Not found. Skipping.".format(file_response.status_code))

                            continue                                 
                            
                        else:
                            helper.log_error("[-] EVENTS: file status_code: {}. Exiting.".format(file_response.status_code))

                            sys.exit()    
                            
                
                    del data["data"]["files"]
                    data["data"].update({"files": files})
                
                #############################
                # Fetch Room Information
                if fetch_room_information == True and data["data"].get("roomId") != None and data["data"].get("roomType") == 'group':
                    
                    helper.log_debug("[-] EVENTS: Found roomId files. Fetching Title")
                    
                    roomId = data["data"].get("roomId")
                    
                    helper.log_debug("[-] EVENTS: roomId: {}".format(roomId))
                    
                    room_url = 'https://api.ciscospark.com/v1/rooms/{}'.format(roomId)
                    
                    room_method = "GET"
                    room_response = helper.send_http_request(room_url, room_method, parameters=None, payload=None, headers=headers, cookies=None, verify=certificate_verification, cert=None, timeout=None, use_proxy=True)

                    helper.log_debug("[-] EVENTS: Room response: {}".format(room_response.status_code))
                    
                    if room_response.status_code >=200 and room_response.status_code <300:
                        helper.log_debug("[-] EVENTS: Room response: {}".format(room_response.json()))
                        room_response_dict = room_response.json()
                        
                        room_title = room_response_dict.get("title")
                        data["data"].update({"roomTitle": room_title})

                        
                    elif room_response.status_code == 404:
                        helper.log_error("[-] EVENTS: room status_code: {}. Not found. Skipping.".format(room_response.status_code))
                        continue                                 
                            
                    else:
                        helper.log_error("[-] EVENTS: room status_code: {}. Exiting.".format(room_response.status_code))

                        sys.exit()
                                     
                event = helper.new_event(data=json.dumps(data), host=host, index=index, source=source, sourcetype=sourcetype)
                ew.write_event(event)

                # Update last_run Checkpoint 
                # compare checkpoint_time with current event's created time
                # update checkpoint_time if the currents event's created time larger than checkpoint_time
                checkpoint_time = helper.get_check_point(checkpoint_name)
                checkpoint_time = datetime.datetime.strptime(checkpoint_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                this_event_created_time = datetime.datetime.strptime(data['created'], '%Y-%m-%dT%H:%M:%S.%fZ')
                helper.log_debug("[-] EVENTS: checkpoint_time vs this_event_created_time: {} vs {}".format(checkpoint_time, this_event_created_time))
                if this_event_created_time > checkpoint_time:
                    checkpoint_time = this_event_created_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    helper.log_debug("[-] EVENTS: updated checkpoint_time: {}".format(checkpoint_time))
                    helper.save_check_point(checkpoint_name, checkpoint_time)
                    helper.log_debug("[-] EVENTS: Storing new checkpoint")

            # Handle Paging
            
            link = json.dumps(response_headers.get("Link"))
            
            if link is not None and link is not "null":
                
                helper.log_debug("[-] EVENTS: link (next): {}.".format(link))
            
                events_url = link[2:].replace(r'>; rel=\"next\""','')
                helper.log_debug("[-] EVENTS: events_url (next): {}.".format(events_url))
            
            else:
                paging = False
            
    helper.log_info("[-] EVENTS: Finished.")
