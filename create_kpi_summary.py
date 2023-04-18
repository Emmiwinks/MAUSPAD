import json
import random
from mauspad_score import *

with open('simfin_data/company_list.json') as user_file:
    file_contents = user_file.read()

n = 0

while n < 10:
    load = json.loads(file_contents)
    companies = load["data"]
    symbol = random.choice(companies)[1]
    m_score = Mauspad_score(symbol, '2012-01-01', '2022-12-31')
    n += 1
