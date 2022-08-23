import json
import urllib.parse
import requests


from requests.adapters import HTTPAdapter, Retry

from typing import Literal

AUTOSAVE_INTERVAL = 50


def loadSiteData(type: Literal["current", "future"]) -> list[dict]:
    with open(f"sites_{type}.json", "r") as f:
        return json.loads(f.read())


def writeSiteData(type: Literal["current", "future"], data: list[dict]) -> None:
    with open(f"sites_{type}_with_operator.json", "w") as f:
        f.write(json.dumps(data))


def generateFeatureInfoUrl(type: Literal["current", "future"], site: dict) -> str:
    # translation: "masts in use" or "masts in future"
    layerName = "MasteIBrug" if type == "current" else "MasteIFremtid"

    offset = 0.000001

    lat1 = site["lat"] - offset
    lat2 = site["lat"] + offset
    lon1 = site["lon"] - offset
    lon2 = site["lon"] + offset

    baseUrl = "https://mastedatabasen.dk/viskort/WMS2.ashx"
    params = {
        "service": "WMS",
        "version": "1.3.0",
        "request": "GetFeatureInfo",
        "query_layers": f"mastedatabasen:{layerName}",
        "layers": f"mastedatabasen:{layerName}",
        # "cql_filter": f"TjenesteArtID=2 AND TeknologiID={site['TeknologiID']}",
        "info_format": "application/json",
        "feature_count": "100",
        "infoidx": "0",
        "crs": "CRS:84",
        "styles": "",
        "width": "1",  # width of "image"
        "height": "1",  # height of "image"
        "i": "1",  # x coord in "image" to pull from
        "j": "1",  # y coord in "image" to pull from
        "bbox": f"{lon1},{lat1},{lon2},{lat2}",
    }

    return f"{baseUrl}?{urllib.parse.urlencode(params)}"


def fetchSitesMetadata(sites: list[dict]) -> list[dict]:
    sitesById = {}

    s = requests.Session()

    retries = Retry(total=20, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])

    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.mount("https://", HTTPAdapter(max_retries=retries))

    for site in sites:
        sitesById[site["masteId"]] = site

    sitesToFetch = list(filter(lambda site: not ("operator" in site), sites))

    print(f"Determined {len(sitesToFetch)} as sites requiring operator data...")

    for num, site in enumerate(sitesToFetch, start=1):
        if num % AUTOSAVE_INTERVAL == 0:
            print("Performing autosave...")
            writeSiteData("current", list(sitesById.values()))
            print("Saved!")

        print(
            f"Fetching operator for site {site['masteId']}... ({num}/{len(sitesToFetch)})"
        )

        if site["masteId"] in sitesById and "operator" in sitesById[site["masteId"]]:
            print(f"Skipping site {site['masteId']} - already has operator data...")
            continue

        url = generateFeatureInfoUrl("current", site)
        resp = s.get(url, timeout=10).json()

        ops = operator_dict_gen(resp["features"])

        for masteId, operator in ops.items():
            if masteId in sitesById:
                sitesById[masteId]["operator"] = operator

    return list(sitesById.values())


def operator_dict_gen(metadata: list[dict]) -> dict:
    operators = {}

    for data in metadata:
        # {
        # Name: "Hi3G Denmark ApS",
        # Fb: "900",
        # type: "Feature",
        # id: "MasteIBrug.fid--452bf9a_182c752a397_-4833",
        # geometry: {
        # type: "Point",
        # coordinates: [
        # 551290,
        # 6221696
        # ]
        # },
        # geometry_name: "Geografisk_placering",
        # properties: {
        # MasteID: 4913841,
        # Unik_Station_navn: "JC0655D",
        # Idriftsaettelsesdato: "2020-10-19T22:00:00Z",
        # Vejnavn: "Skovrodsvej",
        # Husnummer: "37",
        # Vejkode: "Ukendt",
        # Kommunekode: "Ukendt",
        # Postnr: "8670",
        # By: "Låsby",
        # TjenesteArtID: 2,
        # TeknologiID: 7,
        # Objekt_type: "",
        # Radius_i_meter: -1,
        # UTM_E: 551290,
        # UTM_N: 6221696,
        # TjenesteArt_navn: "Mobiltelefoni",
        # Teknologi_navn: "UMTS",
        # Frekvensbaand: 900
        # }
        # }

        op = data["Name"]

        # Manual fixes to prevent duplicate operators
        if op == "Cibicom Mobility":
            op = "Cibicom"

        operators[data["properties"]["MasteID"]] = data["Name"]

    return operators


def main() -> None:
    print("Loading sites from file...")

    sites = loadSiteData("current")

    print(f"Loaded {len(sites)} sites!")

    newSites = fetchSitesMetadata(sites)

    writeSiteData("current", newSites)


if __name__ == "__main__":
    main()
