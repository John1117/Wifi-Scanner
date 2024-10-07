import pandas as pd
from function import connect_scanner, receive_scanner_data


host = input("Server IP address (e.g. '192.168.x.x'): ") or '192.168.1.238'
ports = input('List of port nmuber (e.g. [60000, 60001, ...]): ') or [60017, 60018]

devices = {'device': [], 'scanner': [], 'rssi': [], 'time': []}
conns = [False] * len(ports)
addrs = [False] * len(ports)

# Keep connecting to all scanners.
while True:
    for i, port in enumerate(ports):
        if not conns[i]:
            conns[i], addrs[i] = connect_scanner(host, port)

    # While all scanners are connected, keep receiving data from them.
    while all(conns):
        for i, conn, addr in enumerate(zip(conns, addrs)):
            # If connection failed, retry the connection.
            try:
                data = receive_scanner_data(conn, addr)
                # Show the data scanned in this iteration.
                temp_df = pd.DataFrame(data)
                if not temp_df.empty:
                    print(temp_df, '\n')

            except Exception:
                conn.close()
                conns[i] = False
                addrs[i] = False
                print(f'[Error] Connection {addr} failed. Retry connection again.')
                break

            # Extend the scanned data.
            for data_name, data_lst in data.items():
                devices[data_name].extend(data_lst)