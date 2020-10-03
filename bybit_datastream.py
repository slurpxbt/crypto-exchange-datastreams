#######################
# Author: slurpxbt
#######################

from BybitWebsocket import BybitWebsocket
import time
import logging
import datetime as dt



def setup_logger():

    # Prints logger info to terminal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Change this to DEBUG if you want a lot more info
    ch = logging.StreamHandler()

    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger



def main(ws):
    
    ws.subscribe_trade()

    counter = 0
    indicators = {"CVD": 0, "VWAP":0}
    params = {"bids":0, "asks":0, "prc_times_vol":0}
    bid = 0
    ask = 0
    day_ = dt.datetime.today().date()
    while True:
        counter += 1 
        
        if counter == 250:
            ws.ping()
            pong = ws.get_data("pong")
            logger.info(pong)
            counter = 0

        
        data = ws.get_data("trade.BTCUSD")
       
       
        
        if data:

            timestamp = f"{data[0]['timestamp'][:10]} - {data[0]['timestamp'][12:-1]}"
            date = data[0]['timestamp'][:10]
            time_ = data[0]['timestamp'][12:-5]

            current_time = dt.datetime.strptime(time_, "%H:%M:%S").time()
            curret_date = dt.datetime.strptime(date, "%Y-%m-%d").date()

            side = data[0]["side"]
            size = data[0]["size"]
            price = data[0]["price"]

            if side == "Buy":
                params["bids"] += size
            elif side == "Sell":
                params["asks"] += size

            params["prc_times_vol"] += (price * size)

            indicators["VWAP"] = round(params["prc_times_vol"] / (params["bids"] + params["asks"]), 2)
            indicators["CVD"] = round((params["bids"] - params["asks"]) / 10**3, 2)    # unit => thousand




            print(f"time <{curret_date} {current_time}> -> <{side}>\t {size}\t @ {price}\t CVD: {indicators['CVD']}\t VWAP: {indicators['VWAP']}")

        if "curret_date" in locals():
            if day_ != curret_date:
                day_ = curret_date
                indicators = dict.fromkeys(indicators, 0)
                params = dict.fromkeys(params, 0)

            else:
                pass

        time.sleep(0.1)



if __name__ == "__main__":
    logger = setup_logger()
    
    while True:
        
        try:
            ws = BybitWebsocket(wsURL="wss://stream.bybit.com/realtime",api_key="", api_secret="")
            main(ws)
        
        except KeyboardInterrupt:
            ws.exit()
            logger.info("Manually closed datastream")
            break

        except Exception as e:
            logger.info("Exception thrown")
            logger.info(e)
            time.sleep(3)
    


        