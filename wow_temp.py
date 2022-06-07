import requests
r = requests.get("https://raider.io/api/v1/mythic-plus/affixes?region=us&locale=en")
print(r.json()["affix_details"])