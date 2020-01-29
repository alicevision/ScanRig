// ENA-(ENA) stepper motor enable, connected to ground
// DIR-(DIR) motor direction control, connected to ground
// PUL-(PUL) motor step control, connected to ground

# define _MAX_ARG 10
# define _PULSE_PER_REV 800 // number of pulses for making one full cycle rotation
# define _REDUCTION_RATIO 6 // 10/60

# define _EN_5v  4 // ENA+(+5V) stepper motor enable     White
# define _DIR_5v 3 // DIR+(+5v) motor direction control  Brown
# define _STP_5v 2 // PUL+(+5v) motor step control       Yellow

void setup() {
	//Sets the pins as Outputs
	for (int i = 8; i <= 13; i++) { // relai Outputs
		pinMode (i, OUTPUT);
		fastDigitalWrite(i, LOW);
	}

	pinMode (_EN_5v, OUTPUT); // ENA+(+5V)
	pinMode (_DIR_5v, OUTPUT); // DIR+(+5v)
	pinMode (_STP_5v, OUTPUT); // PUL+(+5v)
	
	Serial.begin(9600); //enable Serial Monitor connection in 115200 baud to control from python
	delay(10);
	Serial.flush();
}

// Serial buffer variables
String bufferInput = "";
String bufferStr = "";
bool stringComplete = false;

void serialEvent() {
	while (Serial.available()) {
		char inChar = (char)Serial.read(); // read incoming char from Serial
		if (inChar == '\n') { // end-of-line
			bufferStr = bufferInput;
			stringComplete = true;
			bufferInput = "";
			break;
			// bufferStr = ""; // reset command incoming buffer (allow us to break motor during rotation)
		} else {
			bufferInput += inChar;
		}
	}
}


// advanced digitalWrite function
void fastDigitalWrite(const unsigned int port, bool val) {
	if(port >= 0 && port < 8) {
		val ? PORTD |= (1<<port) : PORTD &= ~(1<<port);
	} else if(port >= 8 && port < 14) {
		//Serial.println(port);
		val ? PORTB |= (1<<(port-8)) : PORTB &= ~(1<<(port-8));
	}
}

String handleReceivedCommand(String str) {
	// command format	cmd:arg01,arg02,...\n
	// return string about error or return :
	// - Success (if cmd success)
	// - Pulse:nb (number of pulse already done if not finish)
	int id;
	String cmdName;
	int argsBuffer[_MAX_ARG];

	id = str.indexOf(':');
	if (id == -1) {
		return "Parsing error: \"" + str + "\"";
	}

	cmdName = str.substring(0, id);
	str = str.substring(id+1);
	
	int argsNb = 0;
	while ( (id = str.indexOf(',') ) != -1 && argsNb < _MAX_ARG) { // for each args passed if found
		argsBuffer[argsNb] = str.substring(0, id).toInt();
		str = str.substring(id+1);
		argsNb++;
	}
	// read arg if needed (because of stop condition in while for multiple args)
	if(str.length() > 0) {
		argsBuffer[argsNb] = str.toInt();
		str = str.substring(id+1);
		argsNb++;
	}

	int args[argsNb];	
	memcpy(args, argsBuffer, sizeof(args)); // copy argsbuffer array to args array

	// ============================================================
	// ======================== commands ==========================
	// ============================================================
	

	if (cmdName.equals("led")) {
		if (argsNb != 2) {
			return "Invalid number of arguments";
		}else {
			int ledNb = args[0];
			if(ledNb < 1 || ledNb > 6) {
				return "invalid led number (must be in [1, 6])";
			}else {
				return setLedState(ledNb, args[1]);
			}
		}
	}else if (cmdName.equals("leftSmooth") || cmdName.equals("rightSmooth")) {
		if (argsNb < 3) { 
			return "Invalid number of arguments";
		}else {
			return SmoothMove(args[0], cmdName.equals("leftSmooth") ? true : false, args[1], args[2]);
		}
	} else if (cmdName.equals("left") || cmdName.equals("right")) {
		if (argsNb < 2) { 
			return "Invalid number of arguments";
		}else {
			return motorMove(cmdName.equals("left") ? true : false, args[0], args[1]);
		}
	} else if (cmdName.equals("leftCapture") || cmdName.equals("rightCapture")) {
		if (argsNb < 3) { 
			return "Invalid number of arguments";
		}else {
			return motorMoveWithCaptureInterval(cmdName.equals("leftCapture") ? true : false, args[0], args[1], args[2]);
		}
	} else if (cmdName.equals("leftCaptureFull") || cmdName.equals("rightCaptureFull")) {
		if (argsNb < 3) { 
			return "Invalid number of arguments";
		}else {
			return capture(cmdName.equals("leftCaptureFull") ? true : false, args[0], args[1], args[2], args[3]);
		}
	} else if (cmdName.equals("leftManual") || cmdName.equals("rightManual")) {
		if (argsNb < 2) { 
			return "Invalid number of arguments";
		}else {
			return motorMoveManual(cmdName.equals("leftManual") ? true : false, args[0], args[1]);
		}
	} else if (cmdName.equals("stop") or cmdName.equals("s")) {
		// stop motor
		return "Success";
	} else {
		return "Unknown command \"" + cmdName + "\"";
	}

}

String setLedState(int ledNb, int state) {
	fastDigitalWrite(7 + ledNb, (state == 1) ? HIGH : LOW);
	return "Success";
}

String motorMoveManual(bool dir, int pulse, int d) {
	// Enables the motor direction to move
	// LOW : left / HIGH : right
	fastDigitalWrite(_DIR_5v, dir ? LOW : HIGH);
	String r = "Success";
	
	for(int x = 0; x < pulse; x++) {
		fastDigitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(d);
		fastDigitalWrite(_STP_5v, LOW); 
		delayMicroseconds(d);
		if(Serial.available()) { // break if incoming data in serial
			r = "Pulse:";
			r.concat(x+1);
			break;
		}
	}
	return r;
}

// leftCaptureFull:360,45,30,15
String capture(bool dir, unsigned long degres, unsigned long captureDegres, unsigned long loadDegres, unsigned long durationForOneTurn) {
	String r = "Success";
	r = SmoothMove(true, dir, loadDegres, durationForOneTurn);
	if( r != "Success" ) { return r; }
	r = motorMoveWithCaptureInterval(dir, degres, captureDegres, durationForOneTurn);
	if( r != "Success" ) { return r; }
	r = SmoothMove(false, dir, loadDegres, durationForOneTurn);
	if( r != "Success" ) { return r; }
	r = SmoothMove(true, !dir, loadDegres, durationForOneTurn);
	if( r != "Success" ) { return r; }
	r = motorMove(!dir, degres, durationForOneTurn);
	if( r != "Success" ) { return r; }
	r = SmoothMove(false, !dir, loadDegres, durationForOneTurn);
	return r;
}

String SmoothMove(bool inOut, bool dir, unsigned long degres, unsigned long durationForOneTurn) {
	fastDigitalWrite(_DIR_5v, dir == true ? LOW : HIGH); // setup dir
	String r = "Success";
	unsigned long  microSecPerMotorTurn = (unsigned long)(1000000) * durationForOneTurn / _REDUCTION_RATIO;
	unsigned long demiStepDuration = microSecPerMotorTurn / _PULSE_PER_REV / 2;
	unsigned long pulseNb = (degres * _REDUCTION_RATIO * _PULSE_PER_REV) / 360;

	for(unsigned x = 0; x < pulseNb; x++) {
		float inOutDirection = inOut ? 1.0 : -1.0;
		float i = easeSigmoid(inOutDirection * (float(x)/float(pulseNb) - 0.5));
		float iterpolatedDuration = float(demiStepDuration) * i;
		fastDigitalWrite(_STP_5v, HIGH);
		delayMicroseconds((unsigned long)(iterpolatedDuration));
		fastDigitalWrite(_STP_5v, LOW); 
		delayMicroseconds((unsigned long)(iterpolatedDuration));
		if(Serial.available()) { // break if incoming data in serial
			r = "AngleDone:";
			r.concat((x+1) * 360 / (_REDUCTION_RATIO * _PULSE_PER_REV) );
			break;
		}
	}
	return r;
}

String motorMove(bool dir, unsigned long degres, unsigned long durationForOneTurn) {
	// Enables the motor direction to move
	// LOW : left / HIGH : right
	// durationForOneTurn in s 
	// degres in degres
	fastDigitalWrite(_DIR_5v, dir == true ? LOW : HIGH); // setup dir
	String r = "Success"; 
	// Calculation of the different variables from the speed and rotation angle passed as parameters
	unsigned long  microSecPerMotorTurn = (unsigned long)(1000000) * durationForOneTurn / _REDUCTION_RATIO;
	unsigned long demiStepDuration = microSecPerMotorTurn / _PULSE_PER_REV / 2;
	unsigned long pulseNb = (degres * _REDUCTION_RATIO * _PULSE_PER_REV) / 360;
	for(unsigned x = 0; x < pulseNb; x++) {
		fastDigitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(demiStepDuration);
		fastDigitalWrite(_STP_5v, LOW); 
		delayMicroseconds(demiStepDuration);
		if(Serial.available()) { // break if incoming data in serial
			r = "Pulse:";
			r.concat(x+1);
			break;
		}
	}
	return r;
}

String motorMoveWithCaptureInterval(bool dir, unsigned long degres, unsigned long captureDegres, unsigned long durationForOneTurn) {
	// Enables the motor direction to move
	// LOW : left / HIGH : right
	// durationForOneTurn in s 
	// degres in degres
	fastDigitalWrite(_DIR_5v, dir == true ? LOW : HIGH); // setup dir
	String r = "Success"; 
	// Calculation of the different variables from the speed and rotation angle passed as parameters
	unsigned long  microSecPerMotorTurn = (unsigned long)(1000000) * durationForOneTurn / _REDUCTION_RATIO;
	unsigned long demiStepDuration = microSecPerMotorTurn / _PULSE_PER_REV / 2;
	unsigned long pulseNb = (degres * _REDUCTION_RATIO * _PULSE_PER_REV) / 360;
	unsigned long pulseCaptureNb = (captureDegres * _REDUCTION_RATIO * _PULSE_PER_REV) / 360;

	for(unsigned x = 0; x < pulseNb; x++) {
		fastDigitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(demiStepDuration);
		fastDigitalWrite(_STP_5v, LOW); 
		delayMicroseconds(demiStepDuration);
		if(x!= 0 && x%pulseCaptureNb == 0) {
			Serial.println("Capture");
		}
		if(Serial.available()) { // break if incoming data in serial
			r = "AngleDone:";
			r.concat((x+1) * 360 / (_REDUCTION_RATIO * _PULSE_PER_REV) );
			break;
		}
	}
	Serial.println("Capture");
	return r;
}

float easeSigmoid(float t) {
	return 1.5 / (1.0 + exp(10.0 * t )) + 1.0;
}

void loop() {
	delay(1); // wait until receive Serial data
	if (stringComplete) {
		Serial.println(handleReceivedCommand(bufferStr));// handle cmd & print return string in Serial for python
		bufferStr = "";
		stringComplete = false;
	}
	
}
