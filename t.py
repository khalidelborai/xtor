from xtor import Tor, getTorPassHash

with Tor(password="password", port=9050) as tor:
    # print(tor.ip)
    print(tor.client.get("http://api.ipify.org").text)
