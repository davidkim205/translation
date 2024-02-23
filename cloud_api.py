from apis import azure_api, deepl_api, google_api, papago_api

api_dict = {
    "deepl": deepl_api,
    "papago": papago_api,
    "azure": azure_api,
    "google": google_api,
}


def translate_en2ko(api, text):
    result = api_dict[api].translate_en2ko(text)
    return result