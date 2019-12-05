import pandas as pd
import requests
from lxml import html

from ranker import ZacksRanker

ARISTOCRATS_URL = "https://en.wikipedia.org/wiki/S%26P_500_Dividend_Aristocrats"

response = requests.get(ARISTOCRATS_URL)
tree = html.fromstring(response.content)
aristocrats = list()

for i in range(1, 26):
    elem = tree.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr[{}]/td[1]/a/text()'.format(i))
    aristocrats.extend(elem)

result = ZacksRanker().get_for_list(aristocrats)

df = pd.DataFrame(sorted(result.items(), key=lambda x: x[1]), columns=['Symbol', 'Rank'])
print(df)
