html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <link rel="icon" href="data:;base64,=">
    <title> Servo </title>
  </head>
  <body>
    <div class="container">
      <h1> Servo </h1>
      <br>
      <h2> Angle </h2>
      <p> Use the slider to move the servo. </p>
      <br>
      <label>
        <input type="range" id="angle" min="0" max="180" value="%d" oninput="oninputEvent(event)">
        <span id="angle_value"> 0 </span> &#176
      </label>
      <br><br>
      <h2> Calibration </h2>
      <p> Place slider on 0 or 180 degrees and adjust minimum or maximum duty cycle values
          until the angle of the servo position matches either 0 or 180 degrees. Record these
          values for use in your program when connecting to this specific servo.
      <br><br>
      <label>
        <input type="number" id="duty_cycle" value="%.3f" min=0 max=1 step=0.001 oninput="oninputEvent(event)">
        Duty cycle
      </label>
      <br>
      <label>
        <input type="number" id="min_duty_cycle" value="%.3f" min=0 max=1 step=0.001 oninput="oninputEvent(event)">
        Minimum duty cycle
      </label>
      <br>
      <label>
        <input type="number" id="max_duty_cycle" value="%.3f" min=0 max=1 step=0.001 oninput="oninputEvent(event)">
        Maximum duty cycle
      </label>
    </div>
  </body>
  <script>
    "use strict";

    function oninputEvent(event) {
      var element = event.target;
      var xmlhttp = new XMLHttpRequest();

      xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          // keep the slider and duty cycle field in sync
          if (element.id == "angle") {
            document.getElementById("duty_cycle").value = parseFloat(this.responseText);
            document.getElementById("angle_value").innerText = element.value;
          }
          if (element.id == "duty_cycle") {
            document.getElementById("angle").value = parseInt(this.responseText);
            document.getElementById("angle_value").innerText = parseInt(this.responseText);
          }
        }
      }

      xmlhttp.open("GET", "set?".concat(element.id, "=", element.value), true);
      xmlhttp.send()
    }

    function onLoadEvent() {
      document.getElementById("angle_value").innerText = document.getElementById("angle").value
    }

    window.onload = onLoadEvent();
  </script>
</html>
"""

if __name__ == "__main__":
    from machine import Pin, PWM
    import socket
    import url
    import gc

    # servo setup
    angle = 90
    min_duty_cycle = 0.025
    max_duty_cycle = 0.121


    def angle_to_duty_cycle(angle):
        return min_duty_cycle + ((max_duty_cycle - min_duty_cycle) / 180) * angle


    def duty_cycle_to_angle(duty_cycle):
        return int((duty_cycle - min_duty_cycle) / ((max_duty_cycle - min_duty_cycle) / 180))


    duty_cycle = angle_to_duty_cycle(angle)

    pwm = PWM(0, frequency=50)
    servo = pwm.channel(0, pin=Pin.exp_board.G15, duty_cycle=duty_cycle)

    # webserver setup
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(socket.getaddrinfo('0.0.0.0', 80)[0][-1])
    serversocket.listen()

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

        conn.write("HTTP/1.1 200 OK\nConnection: close\nServer: WiPy\nContent-Type: text/html\n\n")

        request = url.request(request_line)

        if request["path"] == "/":
            # use printf-style formatting to avoid problems with javascript braces
            conn.write(html % (angle, duty_cycle, min_duty_cycle, max_duty_cycle))

        if request["path"] == "/set":
            parameters = request["parameters"]

            if "duty_cycle" in parameters:
                duty_cycle = float(parameters["duty_cycle"])
                angle = duty_cycle_to_angle(duty_cycle)
                servo.duty_cycle(duty_cycle)
                conn.write("{}".format(angle))

            if "angle" in parameters:
                angle = int(parameters["angle"])
                duty_cycle = angle_to_duty_cycle(angle)
                servo.duty_cycle(duty_cycle)
                conn.write("{0:.3f}".format(duty_cycle))

            if "min_duty_cycle" in parameters:
                min_duty_cycle = float(parameters["min_duty_cycle"])
                duty_cycle = angle_to_duty_cycle(angle)
                servo.duty_cycle(duty_cycle)

            if "max_duty_cycle" in parameters:
                max_duty_cycle = float(parameters["max_duty_cycle"])
                duty_cycle = angle_to_duty_cycle(angle)
                servo.duty_cycle(duty_cycle)

        conn.write("\n")
        conn.close()
