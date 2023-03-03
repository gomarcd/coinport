import sys, time, locale, json
from os import system, name, path
from pycoingecko import CoinGeckoAPI
import pandas as pd
from sty import fg, bg, ef, rs, Style, RgbFg
from tabulate import tabulate

################################################# configuration #
coin_list = 'coinlist.json'
coinport_config = 'conf.json'
with open(coinport_config) as config_file:
    coinport_config_data = json.load(config_file)
    spreadsheet = coinport_config_data['spreadsheet']['filepath']
    user_currency = coinport_config_data['stats']['currency']
    enabled_modules = coinport_config_data['modules']
cg = CoinGeckoAPI()
def clear():
    if name == 'nt':
        _ = system('cls')
        system('color')
    else:
        _ = system('clear')
locale.setlocale(locale.LC_ALL, '')
fg.orange = Style(RgbFg(255, 150, 50))
# configuration #################################################

# keep program running, prompt user for spreadsheet filepath if not found
while True:
    if path.isfile(spreadsheet):
        while True:
            # load any changes to config upon refresh
            coinport_config = 'conf.json'
            with open(coinport_config) as config_file:
                coinport_config_data = json.load(config_file)
                spreadsheet = coinport_config_data['spreadsheet']['filepath']
                user_currency = coinport_config_data['stats']['currency']
                enabled_modules = coinport_config_data['modules']

            # load spreadsheet into Pandas dataframe
            df = pd.ExcelFile(spreadsheet).parse(pd.ExcelFile(spreadsheet).sheet_names[0])

            # track coins/balances from spreadsheet
            coins_to_track = df.columns[2:].tolist()
            balances = df.iloc[0:,2:].sum().to_list()

            # get list of coins from CoinGecko only if missing
            if not path.isfile(coin_list):
                allcoins = cg.get_coins_list()
                with open(coin_list, 'w') as coinlist_file:
                    json.dump(allcoins, coinlist_file, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                with open(coin_list) as coinlist_file:
                    allcoins = json.load(coinlist_file)

            coin_ids = []
            symbols = {}
            coin_data = []
            price = {}
            price_24h = {}
            price_7d = {}

            # map coin names to symbol & CoinGecko ID
            for coin in coins_to_track:
                for i in allcoins:
                    if i['name'] == coin:
                        symbols.update({i['symbol']:i['id']})
                        coin_ids.append(i['id'])

            # retrieve data for the followed coins
            coin_data = cg.get_coins_markets(ids=coin_ids, price_change_percentage="7d", vs_currency=user_currency)

            # make data easier to work with
            for data in coin_data:
                price.update({data['symbol']:data['current_price']})
                price_24h.update({data['symbol']:data['price_change_percentage_24h']})
                price_7d.update({data['symbol']:data['price_change_percentage_7d_in_currency']})

            def colorize_percent(num):
                color = fg.red if num < 0 else fg(10,255,10)
                return f'{color}{num:.2f}%' + fg.rs

            # holdings, book, market, profit/loss values
            holdings = dict(zip(symbols.keys(), balances))
            total_book_value = df.iloc[0:,1].sum()
            holdings_market_value = {k:(holdings[k] * price[k]) for k in holdings}
            total_market_value = sum(holdings_market_value.values())
            profit_loss = total_market_value - total_book_value
            profit_loss_percent = colorize_percent((profit_loss/total_book_value)*100)

            clear()

            # load dataset with only the enabled columns as per conf.json
            dataset = []
            for i in holdings:
                modules_to_print = {}
                header_length = 0
                if enabled_modules['tikr']:
                    tikr_module = ['  [ tikr ]',fg.orange + '  [ ' + fg.rs + fg.yellow + ef.bold + i + fg.rs + rs.bold_dim + (fg.orange + ' ' * (4 - len(i)) + ' ]' + fg.rs)]
                    header_length = header_length + len(tikr_module[0])
                    modules_to_print.update({tikr_module[0]:tikr_module[1]})
                if enabled_modules['price']:
                    price_module = ['[ price ]',f'${price[i]:n}']
                    header_length = header_length + len(price_module[0])
                    modules_to_print.update({price_module[0]:price_module[1]})
                if enabled_modules['1d']:
                    daily_module = ['[ 1d ]',colorize_percent(price_24h[i])]
                    header_length = header_length + len(daily_module[0])
                    modules_to_print.update({daily_module[0]:daily_module[1]})
                if enabled_modules['1w']:
                    weekly_module = ['[ 1w ]',colorize_percent(price_7d[i])]
                    header_length = header_length + len(weekly_module[0])
                    modules_to_print.update({weekly_module[0]:weekly_module[1]})
                if enabled_modules['balance']:
                    balance_module = ['[ balance ]',f'{holdings[i]}']
                    header_length = header_length + len(balance_module[0])
                    modules_to_print.update({balance_module[0]:balance_module[1]})
                if enabled_modules['value']:
                    value_module = ['[ value ]',locale.currency(holdings_market_value[i],grouping=True)]
                    header_length = header_length + len(value_module[0])
                    modules_to_print.update({value_module[0]:value_module[1]})
                if enabled_modules['allocation']:
                    alloc = holdings_market_value[i]/total_market_value*100
                    allocation_module = ['[ alloc ]',f'{alloc:.2f}%']
                    header_length = header_length + len(allocation_module[0])
                    modules_to_print.update({allocation_module[0]:allocation_module[1]})

                # length of columns to help align header
                header_length = header_length + 25

                if holdings[i] != 0:
                    dataset.append(modules_to_print)

            # to help selected currency indicator spacing
            profit_loss_length = len(locale.currency(profit_loss,grouping=True)) + len(profit_loss_percent)
            ansi_len = len(fg.red) if profit_loss < 0 else len(fg(10,255,10)) #to calc spacing
            subtract_length = header_length-20 - (profit_loss_length - ansi_len)

            # header displaying profit/loss/book/market values in selected currency
            portfolio_header = (
            f"_"*header_length + "\n\n" +
            fg.orange + '  [ ' + fg.rs + ef.bold + fg.yellow + "p/l" + fg.rs + rs.bold_dim + fg.orange + '  ]    ' + fg.rs  + locale.currency(total_market_value - total_book_value,grouping=True) + " (" + f"{profit_loss_percent}" + ")" + fg.orange + ef.bold + (' ' * subtract_length) + '[ ' + fg.rs + fg.yellow + f'{user_currency}' + fg.rs + fg.orange + ' ]' + fg.rs + rs.bold_dim +
            fg.orange + '\n  [ ' + fg.rs + ef.bold + fg.yellow + "book " + fg.rs + rs.bold_dim + fg.orange + ']    ' + fg.rs + locale.currency(total_book_value,grouping=True) +
            fg.orange + '\n  [' + fg.rs + ef.bold + fg.yellow + f" mrkt " + fg.rs + rs.bold_dim + fg.orange + ']    ' + fg.rs + locale.currency(total_market_value,grouping=True) + "\n" +
            f"_"*header_length + "\n"
            )
            print(portfolio_header)

            # format the data with Tabulate
            dataset_df = pd.DataFrame(dataset)
            print(tabulate(dataset_df,headers=fg.orange + ef.bold + dataset_df.columns + fg.rs +rs.bold_dim + "\n",tablefmt="plain",stralign="left",floatfmt=".6f",showindex=False))

            time.sleep(10)

    # prompt user for valid file until one is provided, then add it to config
    else:
        while not path.isfile(spreadsheet):
            coinport_config_data['spreadsheet']['filepath'] = input("Woops, no spreadsheet found! Please specify filename: ")
            spreadsheet = coinport_config_data['spreadsheet']['filepath']
        with open(coinport_config, 'w') as config_file:
            json.dump(coinport_config_data, config_file, sort_keys=True, indent=4, separators=(',', ': '))
