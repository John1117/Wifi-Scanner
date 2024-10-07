import socket
import datetime


def connect_scanner(host, port):
    """
    Start up a server socket to bind the address (host, port).
    Connect to the scanner that is set to this address.

    :param host: Server IP address (e.g. '192.168.x.x').
    :type host: str
    :param port: Server port number (e.g. 60000) set as the remote port number in scanner.
    :type port: int
    :return: (Socket connected to the scanner, Scanner address)
    :rtype: (socket.socket, tuple)
    """

    # Start up a server binding to the address and listening for connection.
    # The address may already be used if adjacent binding trials is too close in time.
    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    while True:
        try:
            server.bind((host, port))
            server.listen(5)
            print(f'Server starts at {(host, port)}')
            break

        except Exception:
            print('[Error] Server binding failed. The address may already be used. Please wait.')
            continue

    while True:
        try:
            conn, addr = server.accept()
            print(f'Scanner connected at {str(addr)}.')
            return conn, addr

        except Exception:
            print('[Error] Scanner connection failed.')
            continue


# Constant slicing indexes of scanner byte data.
SYN = slice(0, 1)
CTRL = slice(1, 2)
DATA_TYPR = slice(0, 4)
SCANNER_ADDR = slice(4, 8)
DATA_LEN = slice(2, 4)
CHK = slice(4, 5)
SN = slice(5, 6)
SCANNER_MAC = slice(6, 12)

# Constant slicing indexes of scanned data.
DATA_START = int(12)
UNIT_DATA_LEN = int(8)
DEVICE_MAC = slice(0, 6)
RSSI = slice(6, 7)
CH = slice(7, 8)


def receive_scanner_data(conn, addr):
    """
    Receive data from scannerand and process it to dict form.

    :param conn: Socket connecting to the scanner.
    :type conn: socket.socket
    :param addr: Scanner address (e.g. ('192.168.x.x'. 8000))
    :type addr: tuple
    :return: {'device': [], 'scanner': [], 'rssi': [], 'time': []}.
    :rtype: dict
    """
    byte_data = conn.recv(1024)

    # Slice the byte data.
    ctrl = '{:08b}'.format(int(byte_data[CTRL].hex(), base=16))
    data_type = ctrl[DATA_TYPR]
    data_len = int(byte_data[DATA_LEN].hex(), base=16)
    scanner_mac = byte_data[SCANNER_MAC].hex('-')

    data = {'device': [], 'scanner': [], 'rssi': [], 'time': []}
    # '0000' is the data type of scanning surrounding devices.
    if data_type == '0000':
        n_device = data_len // UNIT_DATA_LEN
        print(f'Scanner {scanner_mac} {addr} receives {n_device} device(s).')

        # Append unit data into the data dict.
        for i in range(DATA_START, DATA_START+data_len, UNIT_DATA_LEN):
            unit_data = byte_data[i:i+UNIT_DATA_LEN]
            deivce_mac = unit_data[DEVICE_MAC].hex('-')
            rssi = int(unit_data[RSSI].hex(), base=16)
            time = datetime.datetime.now()

            data['device'].append(deivce_mac)
            data['scanner'].append(scanner_mac)
            data['rssi'].append(rssi)
            data['time'].append(time)
    return data
