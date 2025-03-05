import gzip
import requests
from io import BytesIO
from datetime import date
import logging
import xml.etree.ElementTree as ET

# Constants for NCBI E-utilities
MAX_ARTICLES_PER_QUERY = 1000
EARLIEST_PUB_DATE = "2025"
CURRENT_DATE = date.today().strftime("%Y/%m/%d")
NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

EFETCH_ENDPOINT = "efetch.fcgi"
ESEARCH_ENDPOINT = "esearch.fcgi"

logger = logging.getLogger(__name__)


def fetch_article_xml(database, article_ids):
    """ Fetches article data in XML format by article IDs from NCBI database. """
    params = {"db": database, "retmode": "xml", "id": article_ids}

    try:
        api_response = requests.get(f"{NCBI_BASE_URL}/{EFETCH_ENDPOINT}", params=params)
        api_response.raise_for_status()  # Raises stored HTTPError, if one occurred.
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return None

    return api_response.text


def retrieve_pubmed_file(year, file_number):
    """ Retrieves a specific baseline PubMed file by year and file number. """
    file_url = f"https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed{year}n{file_number}.xml.gz"

    try:
        response = requests.get(file_url)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to download file: {e}")
        return None

    xml_content = gzip.open(BytesIO(response.content)).read()
    return xml_content


def search_recent_articles(database, days_back=7, modified_date_search=False):
    """ Search for article IDs from the last N days, possibly filtering by modification date. """
    params = {
        "db": database,
        "retmode": "xml",
        "retmax": str(MAX_ARTICLES_PER_QUERY),
        "reldate": str(days_back),
        "datetype": "mdat" if modified_date_search else "edat"
    }

    try:
        api_response = requests.get(f"{NCBI_BASE_URL}/{ESEARCH_ENDPOINT}", params=params)
        api_response.raise_for_status()
    except Exception as e:
        print(f"API call failed: {e}")
        return None

    return extract_ids_from_xml(api_response.text)


def search_articles_by_keyword(keyword):
    """ Search for articles by a keyword and retrieve IDs. """
    params = {
        "db": "PubMed",
        "term": keyword,
        "mindate": EARLIEST_PUB_DATE,
        "maxdate": CURRENT_DATE,
        "retmax": str(MAX_ARTICLES_PER_QUERY),
        "retmode": "xml",
        "datetype": "mdat"
    }

    try:
        api_response = requests.get(f"{NCBI_BASE_URL}/{ESEARCH_ENDPOINT}", params=params)
        api_response.raise_for_status()
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return None

    return extract_ids_from_xml(api_response.text)


def extract_ids_from_xml(xml_data):
    """ Parses XML data to extract article IDs. """
    xml_tree = ET.fromstring(xml_data)
    article_ids = [item.text for item in xml_tree.findall(".//Id")]
    total_articles = xml_tree.find(".//Count").text

    if int(total_articles) > MAX_ARTICLES_PER_QUERY:
        print(f"Warning: Retrieved article count exceeds maximum limit of {MAX_ARTICLES_PER_QUERY} articles.")

    return article_ids
