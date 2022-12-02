import json

from typing import Literal


def loadNewSiteData(type: Literal["current", "future"]) -> list[dict]:
    with open(f"sites_{type}.json", "r") as f:
        return json.loads(f.read())


def loadOldSiteDataWithOperator(type: Literal["current", "future"]) -> list[dict]:
    with open(f"sites_{type}_with_operator.json", "r") as f:
        return json.loads(f.read())


def mergeData(newData: list[dict], oldData: list[dict]) -> list[dict]:
    matches = 0

    mergedData = []
    for site in newData:
        if site["masteId"] in oldData:
            oldSite = oldData[site["masteId"]]
            if oldSite["operator"]:
                matches += 1
                site["operator"] = oldSite["operator"]
        mergedData.append(site)

    print(f"Found {matches} matches of {len(newData)} sites")

    return mergedData


def writeMergedDataToOutputFile(mergedData: list[dict]) -> None:
    with open("merged_data.json", "w") as f:
        f.write(json.dumps(mergedData))


newData = loadNewSiteData("current")
oldData = loadOldSiteDataWithOperator("current")

oldDataDict = {site["masteId"]: site for site in oldData}

mergedData = mergeData(newData, oldDataDict)

writeMergedDataToOutputFile(mergedData)
