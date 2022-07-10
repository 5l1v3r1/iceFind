import random, time, sys, os, hmac, struct, datetime, subprocess
from datetime import datetime
from random import randint
import hashlib, base58, binascii, threading, json
import secp256k1 as ice
import multiprocessing, multiprocessing.pool, threading, logging, traceback, concurrent.futures, re
from threading import Lock, Thread, enumerate
from multiprocessing import Pool, Event, Process, Queue, Value, cpu_count

def RandomInteger(minN, maxN):
    return random.randrange(minN, maxN)

def load_settings():
    global coins_to_search, start_range, end_range, arr, stop, settings_config
    filename = "config.json"
    settings_config = json.loads(open(f"{filename}","r").read())
    coins_string = ""

    for coin in settings_config["coins"]:
        if settings_config["coins"][coin]["enabled"] == True:
            coins_to_search.append(coin)
            load_addresses(settings_config["coins"][coin]["address_file"])
    for coin in coins_to_search: coins_string += "  - "+coin+"\n"
    
    addr_count = len(arr)
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    print(f"[{time}] Addresses loaded: " + str(addr_count))
    print(f"""
    
  Change Script Configurations at: \"{filename}\"
""")
    range = settings_config["myRange"]
    start_range = range["min"]
    end_range = range["max"]
    jump_size = settings_config["jump_size"]
    if end_range > 904625697166532776746648320380374280100293470930272690489102837043110636675 or start_range<1:
        print("\n  Invalid range!\n  Change Range at \"config.json\" before executing!\n")
        stop = True
        
    if stop == False:
        print(f"""
  Searching from {start_range} to {end_range}
  
  Magnitude/Jump {jump_size}

  """)  
        

def load_addresses(filename):
    global addresses, arr
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    print(f"[{time}] Creating database from \"{filename}\" ...Please Wait...")
    with open(filename) as in_file:
        for addr in in_file:
            bit_addr = addr.strip()
            arr.add(bit_addr)

def get_page(page):
    global addresses, arr, coins_to_search, found, settings_config, actual_page

    actual_page = page
    #default Values
    max = 904625697166532776746648320380374280100293470930272690489102837043110636675
    stride = 1
    
    num = int(page,10)
    previous = num - 1
    if previous == 0:
        previous = 1
    next = num + stride                
    if next > max:
        next = max
          
    startPrivKey = (num - 1) * 128+1
    starting_key_hex = hex(startPrivKey)[2:].zfill(64)
    if startPrivKey == 115792089237316195423570985008687907852837564279074904382605163141518161494273:
        ending_key_hex = hex(startPrivKey+63)[2:].zfill(64)
    else:
        ending_key_hex = hex(startPrivKey+127)[2:].zfill(64)

    for i in range(0,128):
        dec = int(startPrivKey)
        HEX = "%064x" % dec
        privKey_C = ice.btc_pvk_to_wif(HEX)
        privKey = ice.btc_pvk_to_wif(HEX, False)
        
        starting_key_hex = hex(startPrivKey)[2:].zfill(64)
        privKeyPage = str(int(str(starting_key_hex),16)/128).split(".")[0]
        if startPrivKey == 115792089237316195423570985008687907852837564279074904382605163141518161494336:
            break

        for coin in coins_to_search:
            if coin == "BTC":
                CAddr = ice.privatekey_to_address(0, True, dec).strip()  # Compressed
                UAddr = ice.privatekey_to_address(0, False, dec).strip() # Uncompressed
                SAddr = ice.privatekey_to_address(1, True, dec).strip()  # P2SH
                BAddr = ice.privatekey_to_address(2, True, dec).strip()  # Bech32
                
                if CAddr in arr or UAddr in arr or SAddr in arr or BAddr in arr:
                    found+=1
                    with open("winner.txt", "a", encoding="utf-8") as f:
                        output = f"""\n
=====================================
: Private Key Page                  : {privKeyPage}
: Private Key HEX                   : {starting_key_hex}
: Private Key WIF UnCompressed      : {privKey}
: Private Key WIF Compressed        : {privKey_C}
=====================================
: BTC Address Compressed        : {CAddr}
: BTC Address UnCompressed      : {UAddr}
: BTC Address Bech32            : {BAddr}
: BTC Address Segwit            : {SAddr}
====================================="""
                        f.write(output)
        startPrivKey += 1

    addresses.clear()

def search(typeScan):
    global start_time, total_tested_pages, start_range, end_range, stop, sequencialTypes
    while stop == False:
        try:
            if typeScan==typeScans[0]:
                try:
                    jump_size = settings_config["jump_size"]
                    i = start_range
                    while i<=end_range:
                        get_page(str(i))
                        total_tested_pages += 1
                        i+=jump_size
                except Exception as e:
                    print(str(e))
                stop = True
            elif typeScan==typeScans[1]:
                try:
                    jump_size = settings_config["jump_size"]
                    i = end_range
                    while i>=start_range:
                        get_page(str(i))
                        total_tested_pages += 1
                        i-=jump_size
                except Exception as e:
                    print(str(e))
                stop = True
            elif typeScan==typeScans[2]:
                for i in range(start_range,end_range):
                    try:
                        get_page(str(i))
                        total_tested_pages += 1
                    except Exception as e:
                        print(str(e))
                stop = True
            elif typeScan==typeScans[3]:
                for i in reversed(range(start_range,end_range)):
                    try:
                        get_page(str(i))
                        total_tested_pages += 1
                    except Exception as e:
                        print(str(e))
                stop = True
            elif typeScan==typeScans[4]:
                try:
                    basePage = RandomInteger(start_range,end_range)
                    stSeqRand = basePage-1000
                    edSeqRand = basePage+1000
                    for i in range(stSeqRand,edSeqRand):   
                        get_page(str(i))
                        total_tested_pages += 1
                except Exception as e:
                    print(str(e))
            elif typeScan==typeScans[5]:
                while True:
                    try:
                        page = str(RandomInteger(start_range,end_range))
                        get_page(page)
                        total_tested_pages += 1
                    except Exception as e:
                        print(str(e))
                        break
            elif typeScan==typeScans[6]:
                try:
                    for i in range(start_range,end_range):
                        if i%2==0:
                            get_page(str(i))
                            total_tested_pages += 1
                except Exception as e:
                    print(str(e))
                stop = True
            elif typeScan==typeScans[7]:
                try:
                    for i in reversed(range(start_range,end_range)):
                        if i%2==0:
                            get_page(str(i))
                            total_tested_pages += 1
                except Exception as e:
                    print(str(e))
                stop = True
            elif typeScan==typeScans[8]:
                try:
                    for i in range(start_range,end_range):
                        if i%2!=0:
                            get_page(str(i))
                            total_tested_pages += 1
                except Exception as e:
                    print(str(e))
                stop = True
            elif typeScan==typeScans[9]:
                try:
                    for i in reversed(range(start_range,end_range)):
                        if i%2!=0:
                            get_page(str(i))
                            total_tested_pages += 1
                except Exception as e:
                    print(str(e))
                stop = True
            else:
                break
        except Exception as e:
            print(str(e))

def search_stats():
    global start_time, total_tested_pages, typeScan, coins_to_search, stop, actual_page
    while stop == False:
        now = time.time()
        since_start = now - start_time
        try:
            pages_per_second = int(total_tested_pages/since_start)*10
            addresses_per_second = pages_per_second*128*len(coins_to_search)
        except:
            pages_per_second = 0
            addresses_per_second = (pages_per_second*128)*len(coins_to_search)
        dots = random.choice(["   ",">  ",">> ",">>>"])
        print(" Searching %s [%s Addresses/s - %s Pages/s] | MODE: %s | Actual Page: %s | Found: %s"%(dots,addresses_per_second,pages_per_second,typeScan,actual_page,found), end="\r")

if __name__ == "__main__":
    addresses = list()   
    arr = set()
    found = start_rang = end_range = total_tested_pages = 0
    stop = False
    coins_to_search = []
    start_time = time.time()    
    settings_config = {}
    load_settings()

    if stop == False:
        typeScans = ["Range + Jump [Forward]","Range + Jump [Backward]","Sequencial [Forward]","Sequencial [Backward]","Sequencial + Random","Random","Odd Numbers [Forward]","Odd Numbers [Backward]","Even Numbers [Forward]","Even Numbers [Backward]"]
        scanN = 0
        print("  Please choose how to scan:")
        for scan in typeScans:
            print(" ",scanN,"=>",scan)
            scanN+=1
        
        inputUserTypeScan = -1
        while inputUserTypeScan<0 or inputUserTypeScan>len(typeScans):
            inputUserTypeScan = int(input("\n  Scan Type Number : "))

        typeScan = typeScans[inputUserTypeScan]

        nThreads = 1

        for i in range(nThreads):
            x = threading.Thread(target=search, args=(typeScan,))
            x.start()

    
        x = threading.Thread(target=search_stats)
        x.start()
