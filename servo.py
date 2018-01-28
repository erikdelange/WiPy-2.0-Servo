html = """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <title>WiPy</title>
    </head>
    <body>
        <div class="container">
            <h1>Servo</h1>
            <br>
            <h2>Position</h2>
            <p>Use the slider to move the servo.</p>
            <br>
            <form id="slider">
                <input type="range" value={0} name="position" id="position">
            </form>
            <br><br>
            <h2>Calibration</h2>
            <p>Modify field duty cycle to find the minimum and maximum values<br>
               for your servo and enter these in fields minimum and maximum.</p>
            <br>
            <form id="dutycycle">
                <input type="number" name="dutycycle" id="dutycycle" value={1:.3f} min=0 max=1 step=0.001>
                <label for "dutycycle">Duty cycle</label>
                <br>
                <input type="number" name="min_dutycycle" id="min_dutycycle" value={2:.3f} min=0 max=1 step=0.001>
                <label for "min_dutycycle">Minimum duty cycle</label>
                <br>
                <input type="number" name="max_dutycycle" id="max_dutycycle" value={3:.3f} min=0 max=1 step=0.001>
                <label for "max_dutycycle">Maximum duty cycle</label>
                <br>
                <input type="submit" value="Submit">
            </form>
        </div>
    </body>
    <script>
        var slider = document.getElementById("position");
        slider.oninput = function() {{
            document.getElementById("slider").submit();
        }}
    </script>
</html>
"""


if __name__ == "__main__":
    from machine import Pin, PWM
    import socket
    import url
    import gc

    # setup for the servo
    position=50
    dutycycle = 0.07
    min_dutycycle = 0.03
    max_dutycycle = 0.13

    pwm = PWM(0, frequency=50)
    servo = pwm.channel(0, pin=Pin.exp_board.G22, duty_cycle=dutycycle)

    # setup for the webserver
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(socket.getaddrinfo('0.0.0.0', 80)[0][-1])
    serversocket.listen()

    while True:
        conn, addr = serversocket.accept()

        request = conn.readline()
        print("request:", request)

        conn.recv(2048)

        d = url.extract(request)

        if "dutycycle" in d:
            dutycycle = float(d["dutycycle"])
            position = int((dutycycle - min_dutycycle) / ((max_dutycycle - min_dutycycle) / 100))
            servo.duty_cycle(dutycycle)

        if "position" in d:
            position = int(d["position"])
            dutycycle = min_dutycycle + ((max_dutycycle - min_dutycycle) / 100) * position
            dutycycle = min(max(dutycycle, min_dutycycle), max_dutycycle)
            servo.duty_cycle(dutycycle)

        if "min_dutycycle" in d:
            min_dutycycle = float(d["min_dutycycle"])

        if "max_dutycycle" in d:
            max_dutycycle = float(d["max_dutycycle"])

        response = html.format(position, dutycycle, min_dutycycle, max_dutycycle)
        conn.send(response)
        conn.close()

        gc.collect()
