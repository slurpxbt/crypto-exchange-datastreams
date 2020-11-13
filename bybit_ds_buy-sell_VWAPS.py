#######################
# Author: slurpxbt
#######################

# datastream that detects trapped buyers/sellers
# price above S-VWAP = trapped seller
# price below B-VWAP = trapped buyer
# price in between = range

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
    


    today = dt.datetime.utcnow()

    day_ = today.date()
    hour_ = today.time().hour
    sec_ = today.time().second
    
    # Intraday stats vars ---------------------------------------------------------------
    intraday_indicators = {"B_VWAP":0,"S_VWAP":0, "sell_speed":0, "buy_speed":0}
    intraday_params = {"bids":1, "asks":1, "prc_times_vol_buy":1,"prc_times_vol_sell":1, "daily_stats":False, "D_open":0}
    firts_D_loop = False
    # -----------------------------------------------------------------------------------
    # ping vars
    ping_index = 0
    ping_sec = [0, 20, 40]
    # -----------------------------------------------------------------------------------
    # Hourly vars
    hourly_indicators = {"B_VWAP":0,"S_VWAP":0, "sell_speed":0, "buy_speed":0}
    hourly_params = {"bids":1, "asks":1, "prc_times_vol_buy":1,"prc_times_vol_sell":1}
    # -----------------------------------------------------------------------------------
    data_received = False

    while True: 

        # websocket ping -----------------------------
        cur_time = dt.datetime.utcnow().time()
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

            now = dt.datetime.utcnow()

            curret_date = now.date()
            current_time = now.time()

            for trade in trade_data:
                side = trade["side"]
                size = trade["size"]
                price = trade["price"]

                if firts_D_loop:
                    intraday_params["D_open"] = price
                    firts_D_loop = False

                if side == "Buy":
                    intraday_params["bids"] += size
                    hourly_params["bids"] += size
                    
                    intraday_params["prc_times_vol_buy"] += (price * size)
                    intraday_indicators["B_VWAP"] = round(intraday_params["prc_times_vol_buy"] / intraday_params["bids"] , 2)
                    intraday_indicators["buy_speed"] = round((intraday_params["bids"])  / 24 / 1000, 1)      # k$/h

                    hourly_params["prc_times_vol_buy"] += price * size
                    hourly_indicators["B_VWAP"] = round(hourly_params["prc_times_vol_buy"] / hourly_params["bids"] , 2)
                    hourly_indicators["buy_speed"] = round((hourly_params["bids"])  / 60 /1000, 1)      # k$/h

                elif side == "Sell":
                    intraday_params["asks"] += size
                    hourly_params["asks"] += size

                    intraday_params["prc_times_vol_sell"] += (price * size)
                    intraday_indicators["S_VWAP"] = round(intraday_params["prc_times_vol_sell"] / intraday_params["asks"] , 2)
                    intraday_indicators["sell_speed"] = round((intraday_params["asks"])  / 24 / 1000, 1)      # k$/h

                    hourly_params["prc_times_vol_sell"] += price * size
                    hourly_indicators["S_VWAP"] = round(hourly_params["prc_times_vol_sell"] / hourly_params["asks"] , 2)
                    hourly_indicators["sell_speed"] = round((hourly_params["asks"])  / 60 /1000, 1)      # k$/h

                

         # Intervall prints
        if cur_time.second % 1 == 0 and cur_time.second != sec_  and data_received:
            
            sec_ = cur_time.second

            # ID -> intraday
            # 1H -> hourly
            if not intraday_params["daily_stats"]:
                print(f"<{curret_date} {cur_time.strftime('%H:%M:%S')} UTC> -> price: {price}\t B-VWAP: {intraday_indicators['B_VWAP']}\t S-VWAP: {intraday_indicators['S_VWAP']}\t b-speed: {intraday_indicators['buy_speed']} k$/h\t s-speed: {intraday_indicators['sell_speed']} k$/h \t H1-B-VWAP: {hourly_indicators['B_VWAP']}\t H1-S-VWAP: {hourly_indicators['S_VWAP']}\t H1-b-speed: {hourly_indicators['buy_speed']} k$/h\t H1-s-speed: {hourly_indicators['sell_speed']} k$/h")
            else:
                print(f"<{curret_date} {cur_time.strftime('%H:%M:%S')} UTC> -> price: {price}\t ID_B-VWAP: {intraday_indicators['B_VWAP']}\t ID_S-VWAP: {intraday_indicators['S_VWAP']}\t ID_b-speed: {intraday_indicators['buy_speed']} k$/h\t ID_s-speed: {intraday_indicators['sell_speed']} k$/h \t H1-B-VWAP: {hourly_indicators['B_VWAP']}\t H1-S-VWAP: {hourly_indicators['S_VWAP']}\t H1-b-speed: {hourly_indicators['buy_speed']} k$/h\t H1-s-speed: {hourly_indicators['sell_speed']} k$/h")

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
            ws = BybitWebsocket(wsURL="wss://stream.bytick.com/realtime",api_key="", api_secret="")
            main(ws)
        
        except KeyboardInterrupt:
            ws.exit()
            logger.info("Manually closed datastream")
            break

        except Exception as e:
            logger.info("Exception thrown")
            logger.info(e)
            time.sleep(3)
    


        