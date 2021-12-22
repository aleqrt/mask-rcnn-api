import requests
import json


class DLVServerWrapper:
    def __init__(self, username, password, userId="", urlDlvService = "http://192.168.5.55:30752/ReasoningService/Service"):
        self.urlDlvService = urlDlvService
        self.username = username
        self.password = password
        self.userId = username if userId == "" else userId

    def executeNewProgram(self,program,options=""):
        jsonBody = {}
        jsonBody["userId"]=self.userId
        jsonBody["programContent"] =program
        url = self.urlDlvService+"?action=executeNewProgramDirectly"
        if options:
            jsonBody["options"] =options
            url+="WithOptions"
        response = requests.api.post(url,json=jsonBody,auth=(self.username, self.password))
        print(response)
        results = json.loads(response.content)["resultsObject"]["rawTextResults"]
        return results
        

    def executeProgram(self,filesPaths,options=""):
        jsonBody = {}
        jsonBody["userId"]=self.userId
        jsonBody["program"] ={"filesPaths":filesPaths}
        
        url = self.urlDlvService+"?action=executeProgram"
        if options:
            jsonBody["options"] =options
            url+="WithOptions"
        
        response = requests.api.post(url,json=jsonBody,auth=(self.username, self.password))
        print(response)
        results = json.loads(response.content)["resultsObject"]["rawTextResults"]
        return results
        
    def registerProgram(self,pathProgram,programContent,overwrite=False):
        jsonBody = {}
        jsonBody["userId"]=self.userId
        jsonBody["programFileUri"] =pathProgram
        jsonBody["programContent"] =programContent
        jsonBody["overwriteIfExisting"]=str(overwrite).lower()
        url = self.urlDlvService+"?action=registerProgram"
        
        response = requests.api.post(url,json=jsonBody,auth=(self.username, self.password))
        return response
    
    def removeProgram(self, filesPaths): #filesPaths list of files
        jsonBody = {}
        jsonBody["userId"]=self.userId
        jsonBody["program"] ={"filesPaths":filesPaths}
        url = self.urlDlvService+"?action=removeProgram"
        response = requests.api.post(url,json=jsonBody,auth=(self.username, self.password))
        return response.json

dlvWrapper = DLVServerWrapper("elettrocablaggi","elettrocablaggi")

with open("reasoning.asp", "r") as f:
    reasoning = f.read()

with open("./facts/net1_normalized2.asp", "r") as f:
    netFacts = f.read()
with open("./facts/0A00018253.04_cad_normalized2.asp", "r") as f:
    cadFacts = f.read()

program = '\n'.join([reasoning,cadFacts,netFacts])
#print(program)
results = dlvWrapper.executeNewProgram(program,options="--printonlyoptimum --filter=absent/2")

print(results)

#results = dlvWrapper.executeNewProgram("ciaooooo(1).",options="--filter=ciaooooo/1")
#print(results)



