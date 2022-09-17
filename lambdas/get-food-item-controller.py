import os
import requests

ID_PATH_PARAM = 'id'
ENV_API_KEY = 'API_KEY'
ENV_API_URL = 'API_URL'
NUTRIENT_LIST = (1008,1003,1005,1004)

def lambda_handler(event, context):
    fdc_id = event['pathParameters'][ID_PATH_PARAM]
    api_key = os.environ[ENV_API_KEY]
    api_url = os.environ[ENV_API_URL]

    return get_food_item(api_url, api_key, fdc_id)


def get_food_item(api_url: str, api_key: str, id: str) -> dict:
    request_url = '{url}/food/{id}?api_key={api_key}'.format(
        url = api_url,
        id = id,
        api_key = api_key
    )

    print(request_url)

    response = requests.get(request_url)
    if response.status_code != 200:
        raise BadAPIResponseError(response.status_code)
    response_body = response.json()

    return filter_tracked_nutrients(response_body)


# Nutrient IDs of cals[1008], protein[1003], carbs[1005], fats[1004], water (unitName)
def filter_tracked_nutrients(item: dict, nutrientIDs: tuple = (1008,1003,1005,1004)) -> dict:
    try:
        name = item['brandName']
    except Exception:
        name = item['description']

    id = item['fdcId']
    tracked_nutrients = [x for x in item['foodNutrients'] if x['nutrient']['id'] in nutrientIDs]
    food = {
        'id': id,
        'name': name,
        'nutrients': [{
            'name': x['nutrient']['name'],
            'amount': x['nutrient']['number'],
            'unit': x['nutrient']['unitName']
        } for x in tracked_nutrients]
    }
    return food


# TODO DUPLICATE - add to lambda layer
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
