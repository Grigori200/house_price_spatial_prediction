from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, Request
import pandas as pd
from tqdm import tqdm


def span_info_format(text: str):
    text = text.replace('\xa0', '')
    if 'zł' in text and 'zł/m²' not in text:
        return "price", float(text.replace('zł', '').replace(',', '.'))
    elif ' pokój' in text:
        return "rooms", int(text.replace(' pokój', ''))
    elif ' pokoi' in text:
        return "rooms", int(text.replace(' pokoi', ''))
    elif ' pokoje' in text:
        return "rooms", int(text.replace(' pokoje', ''))
    elif ' m²' in text:
        return "surface", float(text.replace(' m²', '').replace(',', '.'))
    return None, None


def scrapp_otodom(url: str, max_pages: int):
    records = []
    for i in range(1, max_pages + 1):
        req = Request(f'{url}?page={i}', headers={'User-Agent': "Mozilla/5.0"})
        sauce = urlopen(req).read()
        soup = bs(sauce, 'html5lib')
        results = soup.find('main').find('div', {'role': 'main'}).find('div', {'data-cy': 'search.listing.organic'}).findAll \
            ('li')

        with open("./data.txt", "w") as file:
            file.write(results[0].text)

        with open("./data1.txt", "w") as file:
            file.write(results[6].text)

        for idx, li in tqdm(enumerate(results)):
            try:
                info = {}
                for item in li.findAll('span', {"class": "css-1cyxwvy ei6hyam2"}):
                    if item is not None:
                        key, val = span_info_format(item.text)
                        if key is not None:
                            info[key] = val
                info['address'] = li.find('p', {"class": "css-19dkezj e1n06ry53"}).text

                if "price" in info.keys():
                    records.append(info)

            except Exception as e:
                print(e)
    return pd.DataFrame.from_records(records)


if __name__ == "__main__":
    url = 'https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw/wroclaw/wroclaw'
    pages = 259
    out_df = scrapp_otodom(url, pages)
    out_df.to_csv('oto.csv')
