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
    
    today = dt.datetime.today()

    day_ = today.date()
    hour_ = today.time().hour
    sec_ = today.time().second
    
    # Intraday stats vars ---------------------------------------------------------------
    intraday_indicators = {"CVD": 0, "VWAP":0, "buy_sell_ratio":0, "range":0}
    intraday_params = {"bids":1, "asks":1, "prc_times_vol":1, "daily_stats":False, "D_open":0}
    firts_D_loop = False
    # -----------------------------------------------------------------------------------
    # ping vars
    ping_index = 0
    ping_sec = [0, 20, 40]
    # -----------------------------------------------------------------------------------
    # Hourly vars
    hourly_indicators = {"buy_sell_ratio":0}
    hourly_params = {"bids":1, "asks":1}
    # -----------------------------------------------------------------------------------
    data_received = False

    while True: 

        # websocket ping -----------------------------
        cur_time = dt.datetime.today().time()
        # this keep connection alive
        if cur_time.second == ping_sec[ping_index]:
            client.ping()
            #pong = client.get_data("pong")
            #logger.info(pong)

            ping_index +=1
            if ping_index == 3:
                ping_index = 0
        # --------------------------------------------

        # Data Requests --------------------
        trade_data = client.get_data("trade.BTCUSD")
        # --------------------------------------------
        
       
        
        if trade_data:  # if data is returned 
            
            data_received = True

            date = trade_data[0]['timestamp'][:10]
            time_ = trade_data[0]['timestamp'][11:-5]

            current_time = dt.datetime.strptime(time_, "%H:%M:%S").time()
            curret_date = dt.datetime.strptime(date, "%Y-%m-%d").date()

            side = trade_data[0]["side"]
            size = trade_data[0]["size"]
            price = trade_data[0]["price"]


            if firts_D_loop:
                intraday_params["D_open"] = price
                firts_D_loop = False

            if side == "Buy":
                intraday_params["bids"] += size
                hourly_params["bids"] += size
            elif side == "Sell":
                intraday_params["asks"] += size
                hourly_params["asks"] += size


            # intraday indicator calcs
            intraday_params["prc_times_vol"] += (price * size)
            intraday_indicators["VWAP"] = round(intraday_params["prc_times_vol"] / (intraday_params["bids"] + intraday_params["asks"]), 2)   # VWAP
            intraday_indicators["CVD"] = round((intraday_params["bids"] - intraday_params["asks"]) / 10**3, 2)                               # unit => thousands
            intraday_indicators["buy_sell_ratio"] = round(((intraday_params["bids"]/intraday_params["asks"])*100) , 2)                       # buy/sell ratio
            intraday_indicators["range"] = price - intraday_params["D_open"]                                                                 # Intraday range
 
            # hourly indicator calcs
            hourly_indicators["buy_sell_ratio"] = round(((hourly_params["bids"]/hourly_params["asks"])*100) , 2)                             # buy/sell ratio




            # if not intraday_params["daily_stats"]:
            #     print(f"<{curret_date} {current_time}> -> <{side}>\t {size}\t @ {price}\t CVD: {intraday_indicators['CVD']}\t VWAP: {intraday_indicators['VWAP']}\t B/S ratio: {intraday_indicators['buy_sell_ratio']} %\t hourly-B/S ratio: {hourly_indicators['buy_sell_ratio']} %\t range: {intraday_indicators['range']}")
            # else:
            #     print(f"<{curret_date} {current_time}> -> <{side}>\t {size}\t @ {price}\t Intraday-CVD: {intraday_indicators['CVD']}\t Intraday-VWAP: {intraday_indicators['VWAP']} \
            #             \t Intraday-B/S ratio: {intraday_indicators['buy_sell_ratio']} %\t hourly-B/S ratio: {hourly_indicators['buy_sell_ratio']}\t daily-range: {intraday_indicators['range']}")


         # Intervall prints
        if cur_time.second % 5 == 0 and cur_time.second != sec_  and data_received:
            
            sec_ = cur_time.second

            if not intraday_params["daily_stats"]:
                print(f"<{curret_date} {cur_time.strftime('%H:%M:%S')}> -> CVD: {intraday_indicators['CVD']}\t VWAP: {intraday_indicators['VWAP']}\t B/S ratio: {intraday_indicators['buy_sell_ratio']} %\t hourly-B/S ratio: {hourly_indicators['buy_sell_ratio']} %\t range: {intraday_indicators['range']}")
            else:
                print(f"<{curret_date} {cur_time.strftime('%H:%M:%S')}> -> Intraday-CVD: {intraday_indicators['CVD']}\t Intraday-VWAP: {intraday_indicators['VWAP']} \
                        \t Intraday-B/S ratio: {intraday_indicators['buy_sell_ratio']} %\t hourly-B/S ratio: {hourly_indicators['buy_sell_ratio']} %\t\t daily-range: {intraday_indicators['range']}")



        # NARED SE BUY/SELL SPEED PER HOUR



        # restarts indicator each day
        if "curret_date" in locals():       # if current date exists in variables

            # daily indicators reset
            if day_ != curret_date:         # if current(saved) day is different than current date in trade data response
                day_ = curret_date
                intraday_indicators = dict.fromkeys(intraday_indicators, 0)     # set all params in dict to 0
                intraday_params = dict.fromkeys(intraday_params, 1)             # set all params in dict to 1
                intraday_params["daily_stats"] = True                           # change in printing
                firts_D_loop = True                                             # daily loop reset

            else:
                pass
        
            # hourly indicators reset
            if hour_ != current_time.hour:
                hour_ = current_time.hour
                hourly_indicators = dict.fromkeys(hourly_indicators, 0)     # set all params in dict to 0
                hourly_params = dict.fromkeys(hourly_params, 1)             # set all params in dict to 1

            

            
                

        time.sleep(0.05)

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
    


        