html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <link rel="icon" href="data:;base64,=">
    <title> Dual Servo </title>
  </head>
  <body>
    <div class="container">
      <h1> Servo </h1>
      <br>
      <input type="range" id="servo1" min="0" max="180" value="%(angle1)s" oninput="slider(event)">
      <p>Angle <span id="angle1"> %(angle1)s </span> &#176 </p>
      <br>
      <input type="range" id="servo2" min="0" max="180" value="%(angle2)s" oninput="slider(event)">
      <p>Angle <span id="angle2"> %(angle2)s </span> &#176 </p>
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
            document.getElementById("angle1").innerHTML = parseInt(this.responseText);
          if (element.id == "servo2")
             document.getElementById("angle2").innerHTML = parseInt(this.responseText);
        }
      }

      xmlhttp.open("GET", "/set?".concat(element.id, "=", element.value), true);
      xmlhttp.send()
    }
    </script>
</html>
"""

MIN_DUTY_CYCLE = 0.025
MAX_DUTY_CYCLE = 0.121


class Servo:

    def __init__(self, pwm_channel, angle=None):
        self._pwm_channel = pwm_channel
        self._angle = None  # current servo angle, degrees, range from min_angle to max_angle
        self.min_duty_cycle = MIN_DUTY_CYCLE  # duty cycle matching min_angle, range from 0 to 1
        self.max_duty_cycle = MAX_DUTY_CYCLE  # duty cycle matching max_angle, range from 0 to 1
        self.min_angle = 0  # min servo angle, degrees, range from 0 to 360
        self.max_angle = 180  # max servo angle, degrees, range from 0 to 360

        if angle is not None:
            self.angle = max(min(angle, self.max_angle), self.min_angle)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        value = min(max(value, self.min_angle), self.max_angle)
        self._angle = value
        self._pwm_channel.duty_cycle(self.angle_to_duty_cycle(value))

    def angle_to_duty_cycle(self, angle):
        return self.min_duty_cycle + (
                    (self.max_duty_cycle - self.min_duty_cycle) / (self.max_angle - self.min_angle)) * angle


if __name__ == "__main__":
    from machine import Pin, PWM
    import socket
    import url
    import gc

    # servo setup
    pwm = PWM(0, frequency=50)
    servo1 = Servo(pwm.channel(0, pin=Pin.exp_board.G15), angle=90)
    servo2 = Servo(pwm.channel(1, pin=Pin.exp_board.G16), angle=90)

    # webserver setup
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(socket.getaddrinfo('0.0.0.0', 80)[0][-1])
    serversocket.listen(1)

    while True:
        gc.collect()

        conn, addr = serversocket.accept()
        request_line = conn.readline()

        if request_line in [b"", b"\r\n"]:
            print("empty request line from", addr[0])
            conn.close()
            continue

        print("request line", request_line, "from", addr[0])

        while True:
            line = conn.readline()
            if line in [b"", b"\r\n"]:
                break

        conn.sendall("HTTP/1.1 200 OK\nConnection: close\nServer: WiPy\nContent-Type: text/html\n\n")

        request = url.request(request_line)

        if request["path"] == "/":
            conn.write(html % {"angle1": str(servo1.angle), "angle2": str(servo2.angle)})

        if request["path"] == "/set":
            parameters = request["parameters"]

            if "servo1" in parameters:
                servo1.angle = int(parameters["servo1"])
                conn.write(str(servo1.angle))
            elif "servo2" in parameters:
                servo2.angle = int(parameters["servo2"])
                conn.write(str(servo2.angle))

        conn.write("\n")
        conn.close()
