import json
import os
import requests

QUERY_PARAM_PAGE = 'page'
QUERY_PARAM_PAGE_LIMIT = 'page_limit'
QUERY_PARAM_QUERY = 'q'

DEFAULT_PAGE_LIMIT = 50
DEFAULT_PAGE = 0

ENV_API_KEY = 'API_KEY'
ENV_API_URL = 'API_URL'

def lambda_handler(event, context):
    api_key = os.environ[ENV_API_KEY]
    api_url = os.environ[ENV_API_URL]

    # Get the query params
    #   page: 0 to n
    #   page_limit: default to 50
    #   q: search term
    query_params = event['queryStringParameters']

    # Get the page if it exists or get the default
    if query_params[QUERY_PARAM_PAGE] != None:
        page = query_params[QUERY_PARAM_PAGE]
    else:
        page = DEFAULT_PAGE

    # Get the page limit if it exists or get the default
    if query_params[QUERY_PARAM_PAGE_LIMIT] != None:
        size = query_params[QUERY_PARAM_PAGE_LIMIT]
    else:
        size = DEFAULT_PAGE_LIMIT

    # Get the query term
    q = query_params['q']

    try:
        search_results = process_search_request(api_url, api_key, q, page, size)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(search_results)
        }
    except BadAPIResponseError as e:
        print(e)
        return {
            'statusCode': 502
        }

def process_search_request(api_url: str, api_key: str, query: str, page: int, size: int) -> dict:
    # Make request to external API
    request_url = '{url}/foods/search?api_key={key}&query={query}&pageSize={size}&pageNumber={page}'.format(
        url=api_url, key=api_key, query=query, page=page, size=size
    )

    # Fetch data and check status, status must be 200
    response = requests.get(request_url)
    if response.status_code != 200:
        raise BadAPIResponseError(response.status_code)
    response_body = response.json()
    
    return search_response(response_body)

def search_response(body: dict) -> dict:
    current_page = body['currentPage']
    total_pages = body['totalPages']
    total_results = body['totalHits']
    foods = [filter_tracked_nutrients(x) for x in body['foods']]
    return {
        'current_page': current_page,
        'total_pages': total_pages,
        'total_results': total_results,
        'results': foods
    }
  
# Nutrient IDs of cals[1008], protein[1003], carbs[1005], fats[1004], water (unitName)
def filter_tracked_nutrients(item: dict, nutrientIDs: tuple = (1008,1003,1005,1004)) -> dict:
    try:
        name = item['brandName']
    except Exception:
        name = item['description']

    id = item['fdcId']
    tracked_nutrients = [x for x in item['foodNutrients'] if x['nutrientId'] in nutrientIDs]
    food = {
        'id': id,
        'name': name,
        'nutrients': [{
            'name': x['nutrientName'],
            'amount': x['value'],
            'unit': x['unitName']
        } for x in tracked_nutrients]
    }
    return food


class BadAPIResponseError(Exception):
    def __init__(self, code: int, message: str = None) -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        if self.message:
            return 'BadAPIResponseError, {code}: {message}'.format(
                code=self.code, message=self.message
            )
        else:
            return 'BadAPIResponseError, {code}'.format(code=self.code)
