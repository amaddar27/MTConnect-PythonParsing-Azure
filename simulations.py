from helperFunctions import *
import json
import xmltodict

'''
run_simulation_all parses every single dataItem out of the component streams in the Components_set.
You can choose the components you want by manually adding the component stream into Components_set. 
It sends Json data to an Azure hub dataItem by dataItem in the form:
{DEVICE: {COMPONENT ID:{dataItemId:..., @timestamp:... @sequence: ,,,,,,,,,,}}}

Using the standard xml to dict function for each child of the component streams leads to large json files
that can become inconsistent with regards to certain data items' indices when in a list. Thus, it becomes
impossible to use a sql query on azure stream analytics as the indices of the data items will be changing based on the 
number of dataItems updated by the MTConnect agent. 
'''

Components_set = {'Path', 'Controller', 'Linear', 'Rotary'}  # choose which component stream you want


def run_simulation_all(initial, nextSequence, bufferSize):
    if initial:
        url = 'http://mtconnect.mazakcorp.com:5609/current'
        # url = 'https://smstestbed.nist.gov/vds/current'
        # url = 'http://mtconnect.mazakcorp.com:5609/sample?path=//Path/DataItems/DataItem%5b@type=%22EXECUTION%22%5d'
    else:
        url = 'http://mtconnect.mazakcorp.com:5609/sample?from=' + nextSequence + '&count=' + bufferSize
        # url = 'https://smstestbed.nist.gov/vds/sample?from=' + nextSequence + '&count=' + bufferSize

    dom = getDom(url, max_retries=1)  # try connection to agent
    components = dom.getElementsByTagName('ComponentStream')
    for component in components:
        device = component.parentNode.getAttribute('name')
        try:
            if component.getAttribute('component') in Components_set:
                for rows in component.childNodes:
                    if rows.nodeType == 1:  # 1 = element node, 2 = attribute node, 3 = text node
                        data = json.dumps(xmltodict.parse(rows.toxml()))
                        data = json.dumps({device: {component.getAttribute('componentId'): data}})
                        sendToAzureHub(data)
        except Exception as ex:
            raise SystemExit(ex)

    return getNextSequence(dom)


'''
run_simulation_execution is a much simpler programme it only sends data concerning the execution state of the machine
{DEVICE:{Status: "ACTIVE", Program: "XY-1234", Timestamp: "2021-11-01T09:30:00.000000"}}
'''


def run_simulation_execution(initial, nextSequence, bufferSize, programs):
    if initial:
        url = 'https://smstestbed.nist.gov/vds/current'
        # url = 'http://mtconnect.mazakcorp.com:5609/current'
        # url = 'http://mtconnect.mazakcorp.com:5609/sample?path=//Path/DataItems/DataItem%5b@type=%22EXECUTION%22%5d'
    else:
        # url = 'http://mtconnect.mazakcorp.com:5609/sample?from=' + nextSequence + '&count=' + bufferSize
        url = 'https://smstestbed.nist.gov/vds/sample?from=' + nextSequence + '&count=' + bufferSize

    dom = getDom(url, max_retries=4)  # try connection to agent
    components = dom.getElementsByTagName('ComponentStream')
    for component in components:
        device = component.parentNode.getAttribute('name')
        statuses = component.getElementsByTagName('Execution')
        programs_stream = component.getElementsByTagName('Program')

        if len(programs_stream) != 0:
            if initial:
                programs.update({device: programs_stream[0].childNodes[0].toxml()})
            elif programs_stream[0].hasChildNodes():
                programs[device] = programs_stream[0].childNodes[0].toxml()

        for s in statuses:
            data = xmltodict.parse(s.toxml())
            status = data['Execution']['#text']
            timestamp = data['Execution']['@timestamp']
            data = {device: {'Status': status, 'Program': programs[device], 'Timestamp': timestamp}}
            data = json.dumps(data)
            sendToAzureHub(data)

    nextSequence, bufferSize = getNextSequence(dom)
    return nextSequence, bufferSize, programs
