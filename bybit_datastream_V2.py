#######################
# Author: slurpxbt
#######################

# datastream that detects trapped buyers/sellers
# price above S-VWAP = trapped seller
# price below B-VWAP = trapped buyer
# price in between = range

#######################
import pybit
import time
import datetime as dt
import pickle
import os
from pathlib import Path
from dhooks import Webhook
import traceback




def send_dis_msg(api_key, msg):
    try:
        hook = Webhook(api_key)
    except Exception:
        pass
    
    try:
        hook.send(msg)
    except Exception:
        pass


def main(client):
    

    root = Path(".")


    today = dt.datetime.utcnow()

    day_ = today.date()
    hour_ = today.time().hour
    sec_ = today.time().second
    
   
    # -----------------------------------------------------------------------------------
    # ping vars
    ping_index = 0
    ping_sec = [0, 20, 40]

    closes_4h = [0, 4, 8, 12, 16, 20]

  
    
    while True: 
        cur_time = dt.datetime.utcnow().time()

        # Risk check
        if cur_time.second == ping_sec[ping_index]:
            #pong = client.get_data("pong")
            #logger.info(pong)



            ping_index +=1
            if ping_index == 3:
                ping_index = 0
        # --------------------------------------------

        trade_data = client.fetch("trade.BTCUSD")
        instrument_data = client.fetch("instrument_info.100ms.BTCUSD")

        if trade_data:  # if data is returned 
            
            data_received = True

            now = dt.datetime.utcnow()

            curret_date = now.date()
            current_time = now.time()

            print(instrument_data["open_interest"])


            for trade in trade_data:
                
                price = trade["price"]
                size = trade["size"]
                side = trade["side"]
                print(side, price, size)

       
      


        # Intervall prints
        # if cur_time.second % 10 == 0 and cur_time.second != sec_  and data_received:
            
        #     sec_ = cur_time.second


        # restarts indicator each day
        if "curret_date" in locals():       # if current date exists in variables
        
            # hourly indicators reset 
            if hour_ != current_time.hour:
                #print("new H")

                

                if current_time.hour in closes_4h:
                    print("NEW 4H close")
                    hour_ = current_time.hour
                   
                    if current_time.hour == 0 or current_time.hour == 12:
                       

                        if current_time.hour == 0:
                            print("NEW 1D close")
                        else:
                            print("NEW 12H close")
                       
                       
                        # reset month on first day of the month
                        if curret_date.day == 1:
                            print("MONTH")
                            

                        # each monday reset weekly OI
                        if curret_date.weekday() == 0:
                            print("NEW WEEKS")
                else:
                    hour_ = current_time.hour
                

        time.sleep(0.05)
        

if __name__ == "__main__":
    
    while True:
        #dis_api_key = ""
        
        try:
            
            ws_endpoint = "wss://stream.bybit.com/realtime"
            subs = ["trade.BTCUSD", 'instrument_info.100ms.BTCUSD']


            ws = pybit.WebSocket(ws_endpoint, subscriptions=subs)
            #dis_msg = "```Datastream succesfully connected```"
            #send_dis_msg(dis_api_key, dis_msg)

            main(ws)
        
        except KeyboardInterrupt:
            ws.exit()
            
            
            #dis_msg = "```algo manually closed [keyboard interrupt]```"
            #send_dis_msg(dis_api_key, dis_msg)
            
            break

        except Exception as e:
            
            traceback.print_exc()
            #dis_msg = "```datastream disconected [EXCEPTION]```"
            #send_dis_msg(dis_api_key, dis_msg)
            #error = f"```error:{e}```"
            #send_dis_msg(dis_api_key, error)
            print("-"*100)
            time.sleep(3)
    