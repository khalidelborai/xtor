from xtor import Tor

tor = Tor.startTor(
    port=9052,
    control_port=9053,
    host="127.0.0.1",
    password="passw0rd",
    init_msg_handler=print,
)

with tor:
    print(tor.ip)
