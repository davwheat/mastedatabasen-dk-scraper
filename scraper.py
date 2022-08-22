import json
import urllib.parse
import requests

from typing import Literal

pageSize = 500


def get_mastedatabasen_result_count(type: Literal["current", "future"]) -> int:
    """
    Fetches the number of results for a potential Mastedatabasen.dk query.
    """

    url = generate_mastedatabasen_api_url(
        type=type,
        page=1,
        additionalParams={"count": 1, "outputFormat": "application/json"},
    )

    response = requests.get(url).json()

    return response["totalFeatures"]


def generate_mastedatabasen_api_url(
    type: Literal["current", "future"],
    page: int,
    additionalParams: dict = {},
) -> str:
    """
    Generate a URL to fetch a page of data from Mastedatabasen.dk.
    """

    startIndex = (page - 1) * pageSize

    # translation: "masts in use" or "masts in future"
    layerName = "MasteIBrug" if type == "current" else "MasteIFremtid"

    baseUrl = "https://mastedatabasen.dk/VisKort/map.ashx/wfs"
    params = {
        "service": "WFS",
        "version": "1.3.0",
        "request": "GetFeature",
        "outputFormat": "application/json",
        "srsName": "CRS:84",  # Use "standard" LatLon for exported coords
        "typeName": f"mastedatabasen:{layerName}",
        "sortby": "MasteID",  # startIndex requires a sort
        "startIndex": startIndex,
        "count": pageSize,
    } | additionalParams

    return f"{baseUrl}?{urllib.parse.urlencode(params)}"


def main():
    print("****************************")
    print("* Mastedatabase.dk Scraper *")
    print("*   github.com/davwheat    *")
    print("****************************")
    print()
    print("Attempting to scrape masts in use...")

    site_count = get_mastedatabasen_result_count(type="current")

    print(f"Found {site_count} sites!")
    print()
    print(f"Beginning scrape. Hope you don't get ratelimited...")

    scrape(type="current", count=site_count)


def write_sites_to_file(type: Literal["current", "future"], sites: list[dict]) -> None:
    with open(f"sites_{type}.json", "w") as f:
        f.write(json.dumps(sites))


def scrape(type: Literal["current", "future"], count: int) -> None:
    """
    Scrape all masts in use or masts in future from Mastedatabasen.dk.
    """

    sites: list[dict] = []

    numOfPages = count // pageSize + 1

    for page in range(1, numOfPages + 1):
        print(f"Scraping page {page}/{numOfPages}...")
        url = generate_mastedatabasen_api_url(type, page)
        response = requests.get(url).json()

        for feature in response["features"]:
            sites.append(flatten_site_data(feature))

        print("Done!")

    write_sites_to_file(type, sites)


def flatten_site_data(site: dict) -> dict:
    """
    Flatten a site dict to a dict with only the fields we want.
    """

    # {
    # type: "Feature",
    # id: "MasteIBrug.fid--452bf9a_182c6f8324b_-45a8",
    # geometry: {
    # type: "Point",
    # coordinates: [
    # 12.29804617,
    # 55.65157736
    # ]
    # },
    # geometry_name: "Geografisk_placering",
    # properties: {
    # MasteID: 3871792,
    # Unik_Station_navn: "1",
    # Idriftsaettelsesdato: "2012-12-30T23:00:00Z",
    # Vejnavn: "Godsbanevej",
    # Husnummer: "",
    # Vejkode: "Ukendt",
    # Kommunekode: "Ukendt",
    # Postnr: "2630",
    # By: "Taastrup",
    # TjenesteArtID: 1,
    # TeknologiID: 40,
    # Objekt_type: "",
    # Radius_i_meter: -1,
    # UTM_E: 707497,
    # UTM_N: 6172235,
    # TjenesteArt_navn: "Andre",
    # Teknologi_navn: "GSM-R",
    # Frekvensbaand: null
    # }
    # }

    serviceTypes = {
        1: "Other",
        2: "Mobile telecoms",
        11: "Technology-neutral",
    }

    technologies = {
        33: "DAB",
        34: "DVB-T",
        35: "FM",
        32: "Fixed wireless access",
        40: "GSM-R",
        30: "Land-based mobile radio",
        31: "Radio chain",
        36: "TV",
        42: "NR",
        39: "GSM",
        29: "LTE",
        41: "TK",
        7: "UMTS",
        38: "Technology-neutral",
        37: "Other",
    }

    return {
        "wfsId": site["id"],
        "lat": site["geometry"]["coordinates"][1],
        "lon": site["geometry"]["coordinates"][0],
        "masteId": site["properties"]["MasteID"],
        "stationName": site["properties"]["Unik_Station_navn"],
        "startDate": site["properties"]["Idriftsaettelsesdato"],
        "houseNumber": site["properties"]["Husnummer"],
        "streetName": site["properties"]["Vejnavn"],
        "town": site["properties"]["By"],
        "vejkode": site["properties"]["Vejkode"],
        "kommunekode": site["properties"]["Kommunekode"],
        "postNumber": site["properties"]["Postnr"],
        "serviceType": serviceTypes[site["properties"]["TjenesteArtID"]],
        "technology": technologies[site["properties"]["TeknologiID"]],
        "frequencyBand": site["properties"]["Frekvensbaand"],
    }


if __name__ == "__main__":
    main()
