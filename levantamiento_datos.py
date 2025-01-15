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


def create_book(structure, message):
    ws_keys=['VOLUME' , 'TIMESTAMP']
    assert(type(message==list))
    assert(type(message[1]==dict))
    for level in message[1]['as']:
        my_level=[float(x) for x in level]
        orden=dict(zip(ws_keys,my_level[1:]))
        structure['BOOKS'][0]['ASKS'][my_level[0]] = orden
    for level in message[1]['bs']:
        my_level=[float(x) for x in level]
        orden=dict(zip(ws_keys,my_level[1:]))
        structure['BOOKS'][0]['BIDS'][my_level[0]] = orden 
    #FALTA ORDENAMIENTO DE DATOS
    sort_book(structure)
    return None


#INPUT: SIDE: STRING CON OPCIONES "BID" Ó "ASK",
#       UPDATES: REGISTRO DEL LIBRO, SE ESPERA FORMADO (PRECIO, VOLUMEN)
#       LIBRO DE ORDENES, PROFUNDIDAS DE ORDENES EN LIBRO
#OUTPUT:NONE
#ACTUALIZA EL LIBRO

def sort_book(structure):
    ws_keys=['VOLUME' , 'TIMESTAMP']
    working_storage_dict={'a': 'ASKS' , 'b': 'BIDS'}
    # Keep the book sorted and limited to the specified depth
    print("ORDENANDO LIBRO")
    for _ , valor in working_storage_dict.items():
        structure["BOOKS"][-1][valor]=dict(
            sorted(structure["BOOKS"][-1][valor].items(), key=lambda key_value: key_value[0],
                reverse=True)
                )
    return None

def update_book(structure, message):
    ws_keys=['VOLUME' , 'TIMESTAMP']
    working_storage_dict={'a': 'ASKS' , 'b': 'BIDS'}
    #EMPEZAMOS POR COPIAR EL LIBRO
    structure["BOOKS"].append(copy.deepcopy( structure["BOOKS"][-1] ))
    """Update the bid or ask side of the order book."""
    for order_type in message[1].keys():
        for order in message[1][order_type]:
            if type(order)==list and  len(order)==3:
                my_order=[float(x) for x in order]# [precio,volumen,timestamps]
                if my_order[1]==0.0:
                    del structure["BOOKS"][-1][working_storage_dict[order_type]][my_order[0]]
                    #encontrar en ultimo elemento de libro la orden de precio correspondiente y eliminar
                else:
                    structure["BOOKS"][-1][working_storage_dict[order_type]][my_order[0]]= dict(zip(ws_keys,my_order[1:3]))
                    #actualizar precio y timestamp
            elif type(order)==list and len(order)==4 and order[-1]=="r":
                my_order=[float(x) for x in order[0:-1]]
                structure["BOOKS"][-1][working_storage_dict[order_type]][my_order[0]]= dict(zip(ws_keys,my_order[1:3]))
            else: None
    sort_book(structure)
    return None
   



#INPUT: LIBRO BID_ASK , PROFUNDIDAD DE ORDENES EN LIBRO
#OUTPUT: NONE
# IMPRIME EN CONSOLA EL LIBRO DE ORDENES BID ASK SEGUN PROFUNDIDAD
def output_book(structure):
    """Display the order book in a tabular format."""
    print("Bid\t\t\t\t\t\tAsk")
    bids=structure['BOOKS'][-1]['BIDS']
    asks=structure['BOOKS'][-1]['ASKS']
    bids_keys=list( structure['BOOKS'][-1]['BIDS'].keys())
    asks_keys= list(structure['BOOKS'][-1]['ASKS'].keys())
    for i in range( max( len(bids_keys), len(asks_keys) ) ) :
        if i < len(bids_keys):
            bid_price, bid_volume = bids_keys[i] , bids[bids_keys[i]]['VOLUME']
        else: 
            bid_price, bid_volume = ("-", "-")
        if i < len(asks_keys): 
            ask_price, ask_volume = asks_keys[i] , asks[asks_keys[i]]['VOLUME'] 
        else:
            ask_price, ask_volume = ("-", "-")
        
        print(f"{bid_price} ({bid_volume})\t\t\t{ask_price} ({ask_volume})")
    
    return None



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
structure = {
    "BOOKS": [
        {
        "ASKS": {},
        "SPREAD": None,
        "BIDS": {}
        }
    ]
}
############ ORDENES STRUCTURE #################################


        
############### WORKING STORAGE SECTION ########################

api_feed = "book"
api_symbol = sys.argv[1].upper()
api_depth = int(sys.argv[2])
api_domain = "wss://ws.kraken.com/"
api_book = {"bid": {}, "ask": {}}
api_data = json.dumps({
"event": "subscribe",
"subscription": {"name": api_feed, "depth": api_depth},
"pair": [api_symbol]
})

#################################################################
############## PROCEDURE DIVISION ##############################
################################################################

 
####################### Main Program#################################

def main(api_data):

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} symbol depth")
        print(f"Example: {sys.argv[0]} xbt/usd 10")
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
            print("DEBUG: ESTE ES EL MENSAJE")
            print(f"\033[33m {message} .\033[0m ")
            print("DEBUG : ESTA ES LA API_DATA")
            print(f"\033[34m {message_data} .\033[0m " )
            if isinstance(message_data, list) and len(message_data) > 1:
                if "as" in message_data[1].keys()  or "bs" in message_data[1].keys() :
                    ###############INICIALIZACION DEL LIBRO ##################
                    print("DEBUG INICIALIZANDO LIBRO")
                    create_book(structure, message_data)
                    print("EL LIBRO ES ACTUALMENTE :" )
                    #print(structure["BOOKS"][-1])
            
                elif "a" in message_data[1].keys() or "b" in message_data[1].keys():
                    print("DEBUG, ACTUALIZANDO LIBRO")
                    update_book(structure, message_data)
                    print("EL LIBRO ES ACTUALMENTE :" )
                    #print(structure["BOOKS"][-1])
            else:
                print("HEARTBEAT")
            output_book(structure)
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




