from PyPDF2 import PdfReader
import requests
import urllib
import sys

def getFileId(pdf_path):
    reader = PdfReader(pdf_path)
    links = []

    # Iterate over pages
    for page in reader.pages:
        if "/Annots" in page:
            # Access annotations
            annotations = page["/Annots"]
            for annot_ref in annotations:
                # Resolve the IndirectObject reference
                annot = annot_ref.get_object()
                if "/A" in annot and "/URI" in annot["/A"]:
                    uri = annot["/A"]["/URI"]  # Extract the URI
                    links.append(uri)

    original_links = []
    for safelink in links:
        # Parse the URL and extract the `url=` parameter
        parsed_url = urllib.parse.urlparse(safelink)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        encoded_url = query_params.get('url', [None])[0]  # Get the first `url` parameter
        if encoded_url:
            decoded_url = urllib.parse.unquote(encoded_url)  # Decode the URL
            original_links.append(decoded_url)
    original_links = list(set(original_links)) #Remove duplicates

    file_id = []
    for link in original_links:
        file_id.append(link.split('/')[-2])
    return file_id

def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download&confirm=1"

    session = requests.Session()

    response = session.get(URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def main():
    pdf_path = "/Users/kausthubhkonuru/Documents/Test-CT-Scans.pdf"
    file_id = getFileId(pdf_path)
    for i, id in enumerate(file_id):
        print(f"Downloading file {i+1} of {len(file_id)}")
        download_file_from_google_drive(id, f"data/CT-Scan-{i+1}.dcm")


if __name__ == "__main__":
    main()