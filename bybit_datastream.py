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



def main(client):
    
    # Websocket subscriptions ------------
    client.subscribe_trade()
    # -----------------------------------
    


    counter = 0
    indicators = {"CVD": 0, "VWAP":0}
    params = {"bids":0, "asks":0, "prc_times_vol":0, "daily_stats":False}
    bid = 0
    ask = 0
    day_ = dt.datetime.today().date()
    while True:
        counter += 1 
        
        # ping -----------------------------
        if counter == 250:
            client.ping()
            pong = client.get_data("pong")
            logger.info(pong)
            counter = 0
        # ----------------------------------

        # Data Requests --------------------
        trade_data = client.get_data("trade.BTCUSD")
        # --------------------------------------------
        
       
        
        if trade_data:  # if data is returned 

            date = trade_data[0]['timestamp'][:10]
            time_ = trade_data[0]['timestamp'][11:-5]

            current_time = dt.datetime.strptime(time_, "%H:%M:%S").time()
            curret_date = dt.datetime.strptime(date, "%Y-%m-%d").date()

            side = trade_data[0]["side"]
            size = trade_data[0]["size"]
            price = trade_data[0]["price"]

            if side == "Buy":
                params["bids"] += size
            elif side == "Sell":
                params["asks"] += size

            params["prc_times_vol"] += (price * size)

            indicators["VWAP"] = round(params["prc_times_vol"] / (params["bids"] + params["asks"]), 2)
            indicators["CVD"] = round((params["bids"] - params["asks"]) / 10**3, 2)    # unit => thousand


            if not params["daily_stats"]:
                print(f"time <{curret_date} {current_time}> -> <{side}>\t {size}\t @ {price}\t CVD: {indicators['CVD']}\t VWAP: {indicators['VWAP']}")
            else:
                print(f"time <{curret_date} {current_time}> -> <{side}>\t {size}\t @ {price}\t Daily-CVD: {indicators['CVD']}\t Daily-VWAP: {indicators['VWAP']}")

        # restarts indicator each day
        if "curret_date" in locals():       # if current date exists in variables
            if day_ != curret_date:         # if current(saved) day is different than current date in trade data response
                day_ = curret_date
                indicators = dict.fromkeys(indicators, 0)
                params = dict.fromkeys(params, 0)
                params["daily_stats"] = True

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
    


        