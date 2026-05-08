import os
import requests
import json


class DLVServerWrapper:
    def __init__(self, username=None, password=None, userId="", urlDlvService=None):
        self.username = username or os.environ.get("DLV_USERNAME", "")
        self.password = password or os.environ.get("DLV_PASSWORD", "")
        self.urlDlvService = urlDlvService or os.environ.get("DLV_SERVICE_URL", "")
        self.userId = self.username if userId == "" else userId

    def executeNewProgram(self, program, options=""):
        jsonBody = {}
        jsonBody["userId"] = self.userId
        jsonBody["programContent"] = program
        url = self.urlDlvService + "?action=executeNewProgramDirectly"
        if options:
            jsonBody["options"] = options
            url += "WithOptions"
        response = requests.api.post(url, json=jsonBody, auth=(self.username, self.password))
        print(response)
        results = json.loads(response.content)["resultsObject"]["rawTextResults"]
        return results

    def executeProgram(self, filesPaths, options=""):
        jsonBody = {}
        jsonBody["userId"] = self.userId
        jsonBody["program"] = {"filesPaths": filesPaths}

        url = self.urlDlvService + "?action=executeProgram"
        if options:
            jsonBody["options"] = options
            url += "WithOptions"

        response = requests.api.post(url, json=jsonBody, auth=(self.username, self.password))
        print(response)
        results = json.loads(response.content)["resultsObject"]["rawTextResults"]
        return results

    def registerProgram(self, pathProgram, programContent, overwrite=False):
        jsonBody = {}
        jsonBody["userId"] = self.userId
        jsonBody["programFileUri"] = pathProgram
        jsonBody["programContent"] = programContent
        jsonBody["overwriteIfExisting"] = str(overwrite).lower()
        url = self.urlDlvService + "?action=registerProgram"

        response = requests.api.post(url, json=jsonBody, auth=(self.username, self.password))
        return response

    def removeProgram(self, filesPaths):
        jsonBody = {}
        jsonBody["userId"] = self.userId
        jsonBody["program"] = {"filesPaths": filesPaths}
        url = self.urlDlvService + "?action=removeProgram"
        response = requests.api.post(url, json=jsonBody, auth=(self.username, self.password))
        return response.json()


if __name__ == '__main__':
    dlvWrapper = DLVServerWrapper()

    with open("reasoning.asp", "r") as f:
        reasoning = f.read()

    with open("./facts/net1_normalized2.asp", "r") as f:
        netFacts = f.read()
    with open("./facts/0A00018253.04_cad_normalized2.asp", "r") as f:
        cadFacts = f.read()

    program = '\n'.join([reasoning, cadFacts, netFacts])
    results = dlvWrapper.executeNewProgram(program, options="--printonlyoptimum --filter=absent/2")

    print(results)
