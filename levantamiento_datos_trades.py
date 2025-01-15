#################################################################
####################IDENTIFICATION DIVISION####################
###############################################################

# PROGRAMADOR : FERNANDO TORRRES
# FECHA : 2025-01-05
# DESCIPCION: ESTE PROGRAMA EXTRAE LA DATA DEL LIBRO DE ORDENES 
#               A TRAVÉS DE LA API DE KRAKEN 
#               ESTE LIBRO DE ORDENES ES DESPLEGADO EN LA CONSOLA




###############################################################
################ENVIROMENT DIVISION ###########################
################################################################

import sys
import os as os
import json
import copy
from websocket import create_connection




################################################################
############ DATA DIVISION #####################################
################################################################

##################PRESENT SCRIPT ADRESS########################

current_dir = os.path.dirname(os.path.abspath(__file__))

############### OUTPUT FILE ADRESS #############################
# Define the JSON file path
OUTPUTBOOK_file_path = os.path.join(current_dir, "output.json")


################ FILE DESCRIPTION #############################



########### OUTPUT FILE STRUCTURE #############################


        
############### WORKING STORAGE SECTION ########################

api_feed = "ticker"
api_symbol = sys.argv[1].upper()
#api_depth = int(sys.argv[2])
api_domain = "wss://ws.kraken.com/"
#api_book = {"bid": {}, "ask": {}}
api_data = json.dumps({
"event": "subscribe",
"subscription": {"name": api_feed },
"pair": [api_symbol]
})
        

#################################################################
############## PROCEDURE DIVISION ##############################
################################################################
 

####################### Main Program#################################


def main(api_data):

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} symbol depth")
        print(f"Example: {sys.argv[0]} xbt/usd")
        sys.exit(1)


    try:
        conn = create_connection(api_domain)
        print("CONEXIÓN INICIALIZADA")
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        sys.exit(1)


    try:
        conn.send(api_data)
        print("ENVIADO EL MENSAJE API_DATA")
    except Exception as e:
        print(f"Feed subscription failed: {e}")
        conn.close()
        sys.exit(1)

    # Start periodic output
    #periodic_output(api_book, api_depth)

   




    message = conn.recv()
    message_data = json.loads(message)
    print("DEBUG: ESTE ES EL MENSAJE RECIBIDO, NO CONTIENE EL LIBRO")
    print(f"\033[33m {message} .\033[0m ")
    print("DEBUG : ESTA ES LA API_DATA, NO CONTIENE EL LIBRO")
    print(f"\033[32m {message_data} .\033[0m ")
    print("SEGUNDA RECEPCION")
    message = conn.recv()
    message_data = json.loads(message)
    print("DEBUG: ESTE ES EL MENSAJE NO CONTIENE EL LIBRO")
    print(f"\033[33m {message} .\033[0m ")
    print("DEBUG : ESTA ES LA API_DATA, NO CONTIENE EL LIBRO")
    print(f"\033[32m {message_data} .\033[0m ")
   
    while True:
        try:
            message = conn.recv()
            message_data = json.loads(message)
            print("DEBUG: ESTE ES EL MENSAJE MAIN LOOP")
            print(f"\033[33m {message} .\033[0m ")
            print("DEBUG : ESTA ES LA API_DATA MAIN LOOP")
            print(f"\033[34m {message_data} .\033[0m " )
            # output_book(structure)
        except KeyboardInterrupt:
            print("\nIMPRIMIENDO LIBRO")
            with open(OUTPUTBOOK_file_path, "w") as json_file:
                 json.dump(structure, json_file, indent=4)
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

    conn.close()

if __name__ == "__main__":
    main(api_data)