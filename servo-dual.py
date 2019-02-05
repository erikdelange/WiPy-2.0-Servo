# zie ook : https://github.com/RinusW/WiPy/tree/master/AiCWebserver

html = """<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
		<link rel="icon" href="data:;base64,=">
		<title> WiPy </title>
	</head>
	<body>
		<div class="container">
			<h1> Servo </h1>
			<br>
			<input type="range" id="servo1" value="%(pos1)s" oninput="slider(event)">
			<p>Position: <span id="position1">%(pos1)s</span></p>
			<br>
			<input type="range" id="servo2" value="%(pos2)s" oninput="slider(event)">
			<p>Position: <span id="position2">%(pos2)s</span></p>
		</div>
	</body>
	<script>
		"use strict";

		function slider(event) {
			var element = event.target;
			var xmlhttp = new XMLHttpRequest();

			xmlhttp.onreadystatechange = function() {
				if (this.readyState == 4 && this.status == 200) {
					if (element.id == "servo1")
						document.getElementById("position1").innerHTML = parseInt(this.responseText);
					if (element.id == "servo2")
						document.getElementById("position2").innerHTML = parseInt(this.responseText);
				}
			}

			xmlhttp.open("GET", "/set?".concat(element.id, "=", element.value), true);
			xmlhttp.send()
		}
	</script>
</html>
"""

class servo:
	# duty cycle limits apply to all servo's
	min_dutycycle = 0.020
	max_dutycycle = 0.128
	step = (max_dutycycle - min_dutycycle) / 100

	def __init__(self, position=50, pwm_channel=None):
		# min_ and max_ limit a servo's position (initally from 0 to 100)
		self.min_position = 0  # unit: %
		self.max_position = 100  # unit: %
		self.position = position  # unit: %
		self.pwm_channel = pwm_channel
		self.move(self.position)

	def move(self, position):
		# apply limits to the new position
		self.position = min(max(position, self.min_position), self.max_position)
		# convert position to duty cycle
		self.dutycycle = servo.min_dutycycle + servo.step * self.position
		self.dutycycle = min(max(self.dutycycle, servo.min_dutycycle), servo.max_dutycycle)
		if self.pwm_channel:
			self.pwm_channel.duty_cycle(self.dutycycle)


if __name__ == "__main__":
	from machine import Pin, PWM
	import socket
	import url
	import gc

	# servo setup
	pwm = PWM(0, frequency=50)
	servo1 = servo(50, pwm.channel(0, pin=Pin.exp_board.G15))
	servo2 = servo(50, pwm.channel(1, pin=Pin.exp_board.G16))

	# for demonstration purpose limit servo2's position
	servo2.min_position = 20
	servo2.max_position = 80

	# webserver setup
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind(socket.getaddrinfo('0.0.0.0', 80)[0][-1])
	serversocket.listen(1)

	while True:
		gc.collect()

		conn, addr = serversocket.accept()
		request_line = conn.readline()

		print("request:", request_line, "from", addr[0])

		if request_line in [b"", b"\r\n"]:
			print("malformed request")
			conn.close()
			continue

		while True:
			line = conn.readline()
			if line in [b"", b"\r\n"]:
				break

		conn.sendall("HTTP/1.1 200 OK\nConnection: close\nServer: WiPy\nContent-Type: text/html\n\n")

		path = url.path(request_line)

		if path == "/":
			conn.sendall(html % { "pos1" : str(servo1.position), "pos2" : str(servo2.position)})

		if path == "/set":
			d = url.query(request_line)

			if "servo1" in d:
				servo1.move(int(d["servo1"]))
				conn.sendall(str(servo1.position))
			elif "servo2" in d:
				servo2.move(int(d["servo2"]))
				conn.sendall(str(servo2.position))

		conn.sendall("\n")
		conn.close()
