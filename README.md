# WiPy-2.0-Servo
Control a servo using a WiPy

### Summary
When using the PWM module controlling a servo with a WiPy requires only a few lines of code. A servo's postion is determined by the width of a pulse. Convention is that a 1.5 ms pulse will place the servo in its neutral (i.e. 90 degree) position. The pulse widths needed to reach the left- and rightmost servo positions (0 and 180 degrees) are normally 1 and 2 ms but can be slightly different per servo. This example shows how to determine these pulse widths and control a servo using a web-interface and Ajax.

### Hardware setup
Servo's are powered by 5V, while the WiPy's outputs operate at 3.3V. The output signal might be sufficient to drive your servo, but if it does not work a 3.3 to 5V level converter is needed. The 5V to power the servo can be taken from pin Vin on the Expansion Board. Make sure to connect the servo's ground to the WiPy (Expansion Board pin GND). You may need an external 5V power supply as some servo's require more current then the Expansion Board can provide via its USB connection. For example I use a DS3115mg digital servo which can draw up to 1A when moving.

### Servo position
The servo I used here is connected to Expansion Board pin G15. Setting up a PWM timer and connecting it to an output pin is very simple and an example can be found in the online Pycom Documentation. The tricky bit is choosing the right values for the PWM frequency and the duty cycle. Most often a PWM frequency of 50 Hz is used which gives a period duration of 20 ms. To place a servo in the neutral position a 1.5 ms pulse width is needed. This cannot be fed directly to the PWM timer as it expects a duty cycle. This is the high-time of the output expressed as percentage of the overall period duration. So to achieve a high-time of 1.5 ms with a period duration of 20 ms the duty cycle must be 1.5 / 20 = 0.075. This is 7.5% but luckily the timer expects the duty cycle as a float between 0 and 1 so it is sufficient to use 0.075.
```python
from machine import Pin, PWM
pwm = PWM(0, frequency=50)  # 50 Hz
servo = pwm.channel(0, pin=Pin.exp_board.G15, duty_cycle=0.075)  # initial duty cycle of 7.5%
servo.duty_cycle(0.10)  # change duty cycle to 10%
```

### Web-interface
The web interface allows you to experiment with various duty cycle values to figure out the ones for the left- and rightmost positions of your servo. Just enter a value in field *Duty cycle*. If the servo still moves you're not yet at the end of its reach. Once you have reached that end-position then enter the current duty cycle value in field *Minimumum duty cycle* or *Maximum duty cycle*.
The slider allows you to move the servo between the minimum and maximum. The slider and the fields use Ajax to communicate with the WiPy, giving the webpage a fast response.

The resulting web page looks like this.

![](https://github.com/erikdelange/WiPy-2.0-Servo/blob/master/ui.png)

The server code is very simple. It just waits for requests, reads the first line, extracts all the parameters from the URL and stores them in a dictionary (see function *url.extract()*). The rest of the request is discarded. If one or more parameters were sent then these are handled accordingly. If the request did not contain a parameter at all (in fact this happens only when you open or refresh the webpage) the html form is returned with the current values for all the variables. I've used Bootstrap 4 to make the form look a little bit nicer.

If you run servo.py from Pymakr the server prints messages to the console so you can keep track of whats going on. This makes debugging easy. Do not forget to move file url.py to the WiPy first.

You need to assign a static IP address to your WiPy to be able to connect from your browser. You have to set this in the WLAN setup of your boot.py. Example code on how to do this can be found in the official Pycom documentation under the WLAN section.

### Two servo's
If you want to control two servo's at the same time use servo-dual.py. It uses the same principles as servo.py. As an extra it contains a class 'servo' so you don't have to duplicate the variables and code to control for every servo. The Ajax web-interface is more simple with just two sliders and for each the current position as a number.
