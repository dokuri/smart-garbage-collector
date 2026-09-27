import network
import socket
import time


# ======= CONFIG =======
WIFI_SSID = "CMF by Nothing Phone 1"
WIFI_PASSWORD = "certified"

# Prefer mDNS name first, then fallback IPs
SERVER_HOSTS = [
	# mDNS (change if needed)
	"10.232.251.113",   # fallback static IP of laptop
]
SERVER_PORT = 6900
PING_PATH = "/ping"
PING_INTERVAL_SEC = 1
CONNECT_TIMEOUT_SEC = 20


def log(msg):
	print("[ESP32]", msg)


def connect_wifi():
	wlan = network.WLAN(network.STA_IF)
	if not wlan.active():
		wlan.active(True)

	if wlan.isconnected():
		log("Wi-Fi already connected: {}".format(wlan.ifconfig()))
		return wlan

	log("Connecting to Wi-Fi SSID: {}".format(WIFI_SSID))
	wlan.connect(WIFI_SSID, WIFI_PASSWORD)

	start = time.time()
	while not wlan.isconnected():
		if time.time() - start > CONNECT_TIMEOUT_SEC:
			log("ERROR: Wi-Fi connect timeout")
			return wlan
		time.sleep(0.5)

	log("Wi-Fi connected: {}".format(wlan.ifconfig()))
	return wlan


def resolve_server():
	for host in SERVER_HOSTS:
		try:
			addr_info = socket.getaddrinfo(host, SERVER_PORT)
			if addr_info:
				addr = addr_info[0][-1]
				log("Resolved server {} -> {}".format(host, addr))
				return host, addr
		except Exception as exc:
			log("ERROR: resolve {} failed: {}".format(host, exc))
	return None, None


def http_ping(host, addr):
	s = None
	try:
		s = socket.socket()
		s.settimeout(5)
		s.connect(addr)
		request = (
			"GET {} HTTP/1.1\r\n"
			"Host: {}\r\n"
			"User-Agent: esp32-micropython\r\n"
			"Connection: close\r\n\r\n"
		).format(PING_PATH, host)
		s.send(request)

		response = s.recv(64)
		if response:
			log("PING ok")
			return True
		log("ERROR: empty response")
		return False
	except Exception as exc:
		log("ERROR: ping failed: {}".format(exc))
		return False
	finally:
		if s:
			try:
				s.close()
			except Exception:
				pass


def main():
	wlan = connect_wifi()

	while True:
		if not wlan.isconnected():
			log("ERROR: Wi-Fi disconnected; reconnecting...")
			wlan = connect_wifi()
			time.sleep(1)
			continue

		host, addr = resolve_server()
		if not addr:
			log("ERROR: no server resolved; retrying")
			time.sleep(2)
			continue

		http_ping(host, addr)
		time.sleep(PING_INTERVAL_SEC)


main()
