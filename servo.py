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
			<h2> Position </h2>
			<p> Use the slider to move the servo. </p>
			<br>
			<form id="slider">
				<input type="range" id="position" name="position" value="%d" oninput="oninputEvent(event)">
			</form>
			<br><br>
			<h2> Calibration </h2>
			<p> Modify field Duty cycle to find the minimum and maximum values for your <br>
			   servo and enter these in fields Minimum - and Maximum duty cycle.
			<br>
			<form id="dutycycle data">
				<input type="number" id="dutycycle" name="dutycycle" value="%.3f" min=0 max=1 step=0.001 oninput="oninputEvent(event)">
				<label for "dutycycle"> Duty cycle </label>
				<br>
				<input type="number" id="min_dutycycle" name="min_dutycycle" value="%.3f" min=0 max=1 step=0.001 oninput="oninputEvent(event)">
				<label for "min_dutycycle"> Minimum duty cycle </label>
				<br>
				<input type="number" id="max_dutycycle" name="max_dutycycle" value="%.3f" min=0 max=1 step=0.001 oninput="oninputEvent(event)">
				<label for "max_dutycycle"> Maximum duty cycle </label>
			</form>
		</div>
	</body>
	<script>
		"use strict";

		function oninputEvent(event) {
			var element = event.target;
			var xmlhttp = new XMLHttpRequest();

			xmlhttp.onreadystatechange = function() {
				if (this.readyState == 4 && this.status == 200) {
					// keep the slider and dutycycle field in sync
					if (element.id == "position")
						document.getElementById("dutycycle").value = parseFloat(this.responseText);
					if (element.id == "dutycycle")
						document.getElementById("position").value = parseInt(this.responseText);
				}
			}

			xmlhttp.open("GET", "set?".concat(element.id, "=", element.value), true);
			xmlhttp.send()
		}
	</script>
</html>
"""


if __name__ == "__main__":
	from machine import Pin, PWM
	import socket
	import url
	import gc

	# servo setup
	position = 50
	dutycycle = 0.07
	min_dutycycle = 0.02
	max_dutycycle = 0.128

	pwm = PWM(0, frequency=50)
	servo = pwm.channel(0, pin=Pin.exp_board.G15, duty_cycle=dutycycle)

	# webserver setup
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind(socket.getaddrinfo('0.0.0.0', 80)[0][-1])
	serversocket.listen()

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
			# use printf-style formatting to avoid problems with javascript braces
			conn.sendall(html % (position, dutycycle, min_dutycycle, max_dutycycle))

		if path == "/set":
			d = url.query(request_line)

			if "dutycycle" in d:
				dutycycle = float(d["dutycycle"])
				position = int((dutycycle - min_dutycycle) / ((max_dutycycle - min_dutycycle) / 100))
				servo.duty_cycle(dutycycle)
				conn.sendall("{}".format(min(max(position,0),100)))

			if "position" in d:
				position = int(d["position"])
				dutycycle = min_dutycycle + ((max_dutycycle - min_dutycycle) / 100) * position
				dutycycle = min(max(dutycycle, min_dutycycle), max_dutycycle)
				servo.duty_cycle(dutycycle)
				conn.sendall("{0:.3f}".format(dutycycle))

			if "min_dutycycle" in d:
				min_dutycycle = float(d["min_dutycycle"])
				conn.sendall("{0:.3f}".format(min_dutycycle))

			if "max_dutycycle" in d:
				max_dutycycle = float(d["max_dutycycle"])
				conn.sendall("{0:.3f}".format(max_dutycycle))

		conn.sendall("\n")
		conn.close()
