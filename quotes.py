from pyppeteer_spider.spider import PyppeteerSpider
from cfg import account_number, password, cookie, account_domain
from lxml.html import fromstring
from datetime import datetime
from pprint import pformat
from pathlib import Path
import random
import aiohttp
import asyncio
import json


def get_endpoint(symbol):
    return f'{account_domain}/?QuotesResearch?P=Quotes&Action=Get+Quote&Symbol={symbol}&Submit=Go'


# login and save cookies.
async def get_cookie(spider,
                     save_path=Path(__file__).joinpath('cookies.json')):
    endpoint = get_endpoint('ES')  # any symbol can be used for getting cookie.
    page = await spider.get(endpoint)
    await asyncio.sleep(random.uniform(2, 3))
    # enter account number.
    account_path = 'table.timeoutLoginTable input[name=A]'
    await page.waitForSelector(account_path)
    await page.type(account_path, account_number, delay=30)
    # enter account password.
    password_path = 'table.timeoutLoginTable input[name=P]'
    await page.waitForSelector(password_path)
    await page.type(password_path, password, delay=30)
    # click submit
    submit_path = '//input[@type="submit"]'
    await page.waitForXPath(submit_path)
    submit_ele = await page.xpath(submit_path)
    await submit_ele[0].click(delay=30)
    await asyncio.sleep(random.uniform(2, 3))
    cookies = await page.cookies()
    await spider.set_idle(page)
    Path(save_path).write_text(json.dumps(cookies, indent=4))


def extract_first(ret):
    if ret:
        return str(ret[0])
    return ""


async def get_quote(root):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    d = {'Datetime': time}
    # find the quote table.
    quote_table_ele = root.xpath('//table[@class="orderTableLargeHeight"]')[0]
    last = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Last")]/following-sibling::td/text()'))
    d['Last'] = last

    change = extract_first(quote_table_ele.xpath('.//tr/td/font/text()'))
    d['Change'] = change

    last_trade = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Last Trade")]/following-sibling::td/text()'
        ))
    d['Last Trade'] = last_trade

    open_ = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Open")]/following-sibling::td/text()'))
    d['Open'] = open_

    bid = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Bid")]/following-sibling::td/text()'))
    d['Bid'] = bid

    tick_vol = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Tick Vol")]/following-sibling::td/text()'))
    d['Tick Vol'] = tick_vol

    high = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"High")]/following-sibling::td/text()'))
    d['High'] = high

    ask = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Ask")]/following-sibling::td/text()'))
    d['Ask'] = ask

    volume = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Volume")]/following-sibling::td/text()'))
    d['Volume'] = volume

    low = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Low")]/following-sibling::td/text()'))
    d['Low'] = low

    exchange = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Exchange")]/following-sibling::td/text()'))
    d['Exchange'] = exchange

    open_int = extract_first(
        quote_table_ele.xpath(
            './/td[contains(text(),"Open Int")]/following-sibling::td/text()'))
    d['Open Int'] = open_int

    return d


async def quote_to_csv(client, endpoint, save_path, sleep_time=0):
    resp = await client.get(
        endpoint,
        headers={
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
            'Cookie': cookie
        })
    html = await resp.text()
    url = str(resp.url)
    print(f"[{str(resp.status)}] {url}")
    root = fromstring(html)
    d = await get_quote(root)
    with save_path.open(mode='a+') as outfile:
        outfile.write(
            f"{d['Datetime']},{d['Last']},{d['Change']},{d['Last Trade']},{d['Tick Vol']},{d['Volume']},{d['Open']},{d['Bid']},{d['High']},{d['Ask']},{d['Low']},{d['Open Int']},{d['Exchange']}\n"
        )
    await asyncio.sleep(sleep_time)
    loop.create_task(quote_to_csv(client, endpoint, save_path, sleep_time))


async def main(loop, symbol_to_save_path):
    client = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    for symbol, save_path in symbol_to_save_path.items():
        endpoint = get_endpoint(symbol)
        loop.create_task(quote_to_csv(client, endpoint, save_path))


if __name__ == "__main__":
    # map symbol to csv path.
    symbol_to_save_path = {}
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop, symbol_to_save_path))
    loop.run_forever()
