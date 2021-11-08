# MTConnect-PythonParsing-Azure
Parsing XML data from online MTConnect agent from: https://smstestbed.nist.gov/vds/current and http://mtconnect.mazakcorp.com/
The goal is to select sections of XML file, and structure them into a JSON format to be avle to be streamed into an Azure SQL databse through an Event or IoT hub.
There are two simulations, one can select potentially every piece of data from the MTConnect agent, the other selects just the execution status of the machine and the current program to calculate utlisation and cycle times
This script does not contain a function to the stream the JSON, and only prints the output to simulate the data being sent to an Azure hub.
