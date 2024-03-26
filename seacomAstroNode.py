__author__ = 'osb holding jsc'

import astronode
import random, sys

_basedir = None
is_micropython = False
is_circuitpython = False
is_cpython = False
is_wifi = False
if sys.implementation.name == "circuitpython":
    is_circuitpython = True
if sys.implementation.name == "micropython":
    is_micropython = True
if sys.implementation.name == "cpython":
    is_cpython = True


try:
    if is_micropython:
        import utime as time
    if is_circuitpython:
        import time
    if is_cpython:
        import time
except:
    sys.exit()

# adding by LamVT
if is_cpython:
    import logging, os
    try:
        basedir = os.path.abspath(os.path.dirname(__file__))
    except:
        basedir = os.getcwd()
    logfilename = os.path.join(basedir, 'AstroNode.log')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(logfilename)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def write_log(msg, error = None):
    global is_micropython
    if is_cpython:
        if error is None:
            logging.info(msg)
        else:
            if hasattr(error, 'message'):
                t_msg = str(error.message)
            else:
                t_msg = str(error)
            logging.info(msg+t_msg)
    if error is None:
        print(msg)
    else:
        print(msg, error)

write_log('starting')
# end of adding

if is_micropython:
    PIN_TX = 15
    PIN_RX = 16
    modem = astronode.ASTRONODE(PIN_TX, PIN_RX)
elif is_circuitpython:
    PIN_TX = 0
    PIN_RX = 1
    modem = astronode.ASTRONODE(PIN_TX, PIN_RX)
else:
    # adding by LamVT
    
    UART_PORT_NAME = "/dev/ttyUSB1"
    UART_PORT_NAME = 'COM7'
    try:
        modem = astronode.ASTRONODE(None, None, UART_PORT_NAME)
    except Exception as e:
        if hasattr(e, 'message'):
            t_msg = str(e.message)
        else:
            t_msg = str(e)
        write_log('error when open UART_PORT_NAME {} '.format(UART_PORT_NAME))
        import sys
        sys.exit('end')

def now_ms():
    if is_micropython:
        return time.ticks_ms()
    else:
        return int(time.time() * 1000)

def sleep_ms(mills):
    if is_micropython:
        time.sleep_ms(mills)
    else:
        time.sleep(mills/1000)

#modem.enableDebugging()

# check if modem is alive
modem_is_alive = False
for x in range(3):
    modem_is_alive = modem.is_alive()
    if modem_is_alive:
        break
    sleep_ms(500)
write_log("modem is alive: {}".format(modem_is_alive))

# read modem info
(status, pn) = modem.product_number_read()
(status, guid) = modem.guid_read()
(status, sn) = modem.serial_number_read()

write_log("Product Number: {}".format(pn))
write_log("GUID: {}".format(guid))
write_log("S/N: {}".format(sn))
# set WiFi dev kit config
# ssid = "<WIFI_SSID>"
# password = "<WIFI_PASS>"
# token = "<ASTOCAST_PORTAL_ACCESS_TOKEN>"
ssid = "OSB GROUP"
password = "Osbhanoi2023$"
ssid = "heroku"
password = "0904266888"
token = "i4zExUSFmLOwHsPNrSTYterRYvvwjkODFE7bzoTYXklAhqOTT5b7C7kQESHwgAxmIKVgcsVlyfewctDy22Zyl3nAOOzdLy1R"
write_log("Setting DevKit wifi credentials and access token")
# DKW2224AS0000018
if sn.find('DKW')>=0:
    is_wifi = True
    write_log("WiFi mode")
    try:
        res = modem.wifi_configuration_write(ssid, password, token)
    except Exception as error:
        write_log("An exception occurred:", error)
else:
    write_log("AstroNode Satelitte mode")

# check modem configuration
(status, config) = modem.configuration_read()
if config.with_pl_ack == 0:
    config.with_pl_ack = 1
    (status, _) = modem.configuration_write(config.with_pl_ack,
                                            config.with_geoloc,
                                            config.with_ephemeris,
                                            config.with_deep_sleep_en,
                                            config.with_msg_ack_pin_en,
                                            config.with_msg_reset_pin_en)
    write_log("configuration changed successfully: {}".format(status == astronode.ANS_STATUS_SUCCESS))
def main():
    # modem._debug_on = True
    is_FirstTime = True
    while True:
        try:
            # write_log("Product Number: {}".format(pn))
            # write_log("GUID: {}".format(guid))
            # write_log("S/N: {}".format(sn))
            # write_log(config.__dict__)
            # send message
            # msg = b'\x01\x02'
            if is_FirstTime:
                is_FirstTime = False
                for i in range(0,8):
                    try:
                        latitude = [17.5602465,9.0413398][random.randrange(0,2)]
                        longitude = [107.8417969, 108.1624418][random.randrange(0,2)]
                        (status, _status) = modem.geolocation_write(latitude,longitude)
                        msg = "First Time {}".format(random.randrange(1,100)).encode()
                        (status, message_id) = modem.enqueue_payload(msg)
                        if status == astronode.ANS_STATUS_SUCCESS:
                            write_log("Message enqueued with id: {}. msg {}".format(message_id, msg))
                    except:
                        pass

            latitude = [17.5602465,9.0413398][random.randrange(0,2)]
            longitude = [107.8417969, 108.1624418][random.randrange(0,2)]
            (status, _status) = modem.geolocation_write(latitude,longitude)
            msg = "hola {}".format(random.randrange(1,100)).encode()
            (status, message_id) = modem.enqueue_payload(msg)
            if status == astronode.ANS_STATUS_BUFFER_FULL:
                write_log("error: message queue is full, will dequeue and then retry")
                (status, message_id) = modem.dequeue_payload()
                if status == astronode.ANS_STATUS_SUCCESS:
                    msg = "test{}".format(random.randrange(1,100)).encode()
                    (status, message_id) = modem.enqueue_payload(msg)
                    if status != astronode.ANS_STATUS_SUCCESS:
                        write_log("unable to enqueque message, error: {}".format(astronode.get_error_code_string(status)))
            write_log("Message enqueued with id: {}. msg {}".format(message_id, msg))
            ack_timeout_ms = 3600000 # 1 hour
            # ack_timeout_ms = 2000 # 5s
            start_timestamp_ms = now_ms()
            end_timestamp_ms = start_timestamp_ms + ack_timeout_ms
            while now_ms() < end_timestamp_ms:
                (status, id) = modem.read_satellite_ack()
                if status == astronode.ANS_STATUS_SUCCESS:
                    write_log("ACK received for message with id: {}".format(id))
                    (status, id) = modem.clear_satellite_ack()
                    if status == astronode.ANS_STATUS_SUCCESS:
                        write_log("ACK cleared")
                    break
                elif status == astronode.ANS_STATUS_NO_ACK:
                    write_log("no ACK received")
                else:
                    write_log("---", status)
                wait_timestamp_ms = now_ms() + 1000
                while now_ms() < wait_timestamp_ms:
                    time.sleep(1)
                    pass
            if is_wifi:
                write_log("WiFi mode - Waiting 180s")
                time.sleep(180)
        except Exception as error:
            write_log("An exception occurred:", error)
            wait_timestamp_ms = now_ms() + 1000
            while now_ms() < wait_timestamp_ms:
                time.sleep(180)
                pass

    print("Hello World!")

if __name__ == "__main__":
    main()
    

