import requests

# data = {
#     'telegram_id': 6,
#     'telegram_link': '@tanacto',
#     'first_name': 'Michael',
#     'last_name': 'Suraev',
#     'birth_date': '2004-11-24',
#     'sex': 'M',
#     'created': '2024-11-24',
#     'updated': '2024-11-27'
# }

params = {
    'telegram_id': '0',
}

response = requests.delete('http://127.0.0.1:8000/deleteUser', params=params)

print(response.json())
