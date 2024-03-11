from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()


@app.get("/get-address/{address}")
async def get_address(address: str):
    url = f"https://www.miamidade.gov/Apps/PA/PApublicServiceProxy/PaServicesProxy.ashx?Operation=GetAddress&clientAppName=PropertySearch&myUnit=&from=1&myAddress={address}&to=200"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception if response status is not 200
        data = response.json()  # Parse JSON response
    except requests.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch address data")

    # Extract relevant information and transform into desired format
    formatted_data = []
    for property_info in data["MinimumPropertyInfos"]:
        formatted_property = {
            "Owner1": property_info["Owner1"],
            "Owner2": property_info["Owner2"],
            "Owner3": property_info["Owner3"],
            "SiteAddress": property_info["SiteAddress"],
            "SiteUnit": property_info["SiteUnit"]
        }
        formatted_data.append(formatted_property)

    # Write data to Google Sheet via SheetDB
    sheetdb_url = "https://sheetdb.io/api/v1/ogwuveyaydqqy"
    try:
        requests.post(sheetdb_url, json=formatted_data)
    except requests.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail="Failed to write data to Google Sheet")

    return {"message": "Data successfully written to Google Sheet"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


