from . import yfapi
from . import iexcloudapi
import os
import json
import time
import threading


def startchecking(ui: object):
    ui.setStatus("Initialize: initializing...")
    if not os.path.exists("./investmentdata"):
        ui.setStatus("Creating main folder...")
        os.mkdir("./investmentdata")
    if not os.path.exists("./investmentdata/master.json"):
        ui.setStatus("Initialize: creating master.json...")
        j = {
            "iextoken": "",
            "symbols": {
                "manual": {},
                "auto": {}
            }
        }
        with open("./investmentdata/master.json", 'w') as f:
            f.write(json.dumps(j, indent=4))
    ui.setStatus("Initialize: Done.")


def update_us_symbols(ui: object):
    # get token
    while True:
        ui.setStatus("Update US Symbols: getting IEX token...")
        with open("./investmentdata/master.json", 'r') as f:
            master = json.loads(f.read())
        token = master["iextoken"]
        try:
            symbols = iexcloudapi.getSymbols(token)
            break
        except:
            countdown = 10
            while countdown >= 0:
                for _ in range(100):
                    ui.setStatus(
                        "Update US Symbols: get token failed. Retry in {}s".format(countdown))
                    time.sleep(0.01)
                countdown -= 1
    # checking
    if not "us" in master["symbols"]["auto"]:
        master["symbols"]["auto"]["us"] = {}
    # disable all auto symbol
    for symbol in master["symbols"]["auto"]["us"]:
        ui.setStatus("Update US Symbols: updating...")
        master["symbols"]["auto"]["us"][symbol] = False
    # enable/add symbols
    for symbol in symbols:
        ui.setStatus("Update US Symbols: updating...")
        master["symbols"]["auto"]["us"][symbol] = True
    # tidy up
    tidy = {}
    for symbol in master["symbols"]["auto"]["us"]:
        ui.setStatus("Update US Symbols: tidying up...")
        if master["symbols"]["auto"]["us"][symbol] == True:
            tidy[symbol] = True
    for symbol in master["symbols"]["auto"]["us"]:
        ui.setStatus("Update US Symbols: tidying up...")
        if master["symbols"]["auto"]["us"][symbol] == False:
            tidy[symbol] = False
    master["symbols"]["auto"]["us"] = tidy
    # save result
    ui.setStatus("Update US Symbols: saving results...")
    with open("./investmentdata/master.json", 'w') as f:
        f.write(json.dumps(master, indent=4))
    ui.setStatus("Update US Symbols: Done.")


def update_price(ui: object):
    ui.setStatus("Download Data: initializing...")
    with open("./investmentdata/master.json", 'r') as f:
        master = json.loads(f.read())
    global symbols
    symbols = []
    for symbol in master["symbols"]["manual"]:
        if master["symbols"]["manual"][symbol] == True:
            ui.setStatus("Download Data: getting symbols...")
            symbols.append(symbol)
    for market in master["symbols"]["auto"]:
        for symbol in master["symbols"]["auto"][market]:
            if master["symbols"]["auto"][market][symbol] == True:
                ui.setStatus("Download Data: getting symbols...")
                symbols.append(symbol)

    def update_robert():
        global symbols
        while len(symbols) > 0:
            symbol = symbols.pop()
            j = yfapi.query(symbol, 1000)
            with open("./investmentdata/{}.json".format(symbol), 'w') as f:
                f.write(json.dumps(j))

    threads = []
    for _ in range(10):
        threads.append(threading.Thread(target=update_robert))
    for thread in threads:
        thread.start()
    while len(symbols) > 0:
        ui.setStatus("Download Data: remaining {}.".format(len(symbols)))
    for thread in threads:
        thread.join()
