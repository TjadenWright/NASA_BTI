url = "rtsp://192.168.166"


parsed_url = urlparse(ip)

username = parsed_url.username
password = parsed_url.password

# Get the IP address from the parsed URL
ip_address = parsed_url.hostname