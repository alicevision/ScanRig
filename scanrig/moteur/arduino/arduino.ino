// ENA-(ENA) stepper motor enable, connected to ground
// DIR-(DIR) motor direction control, connected to ground
// PUL-(PUL) motor step control, connected to ground

#define PI 3.1415926535897932384626433832795
# define _MAX_ARG 10
# define _PULSE_PER_REV 800 // number of pulses for making one full cycle rotation
# define _REDUCTION_RATIO 6 // 10/60

# define _EN_5v  4 // ENA+(+5V) stepper motor enable     White
# define _DIR_5v 3 // DIR+(+5v) motor direction control  Brown
# define _STP_5v 2 // PUL+(+5v) motor step control       Yellow

# define _debugLED 13 // debug led

void setup() {
	//Sets the pins as Outputs
	pinMode (_debugLED, OUTPUT); // debug led already on arduino
	pinMode (_EN_5v, OUTPUT); // ENA+(+5V)
	pinMode (_DIR_5v, OUTPUT); // DIR+(+5v)
	pinMode (_STP_5v, OUTPUT); // PUL+(+5v)
	
	Serial.begin(115200); //enable Serial Monitor connection in 115200 baud to control from python
	serialFlush(); // clean Serial buffer
}

// advanced digitalWrite function
void fastDigitalWrite(const unsigned int port, bool val) {
	if(port >= 0 && port < 8) {
		val ? PORTD |= (1<<port) : PORTD &= ~(1<<port);
	} else if(port >= 8 && port < 14) {
		val ? PORTB |= (1<<port) : PORTB &= ~(1<<port);
	}
}

void serialFlush() {
	while(Serial.available() > 0) {
		Serial.read();
	}
}

// Serial buffer variables
String bufferStr = "";

void serialEvent() {
	char inChar;
	while (Serial.available()) {
		inChar = (char)Serial.read(); // read incoming char from Serial
		if (inChar == '\n') { // end-of-line
			Serial.println(handleReceivedCommand(bufferStr));// handle cmd & print return string in Serial for python
			bufferStr = ""; // reset command incoming buffer (allow us to break motor during rotation)
		} else {
			bufferStr += inChar;
		}
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
	if (id != -1) {
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

		if (cmdName.equals("debugBlink")) { // equalsIgnoreCase
			blinkDebug(); delay(500); blinkDebug();
		} else if (cmdName.equals("leftSmooth") || cmdName.equals("rightSmooth")) {
			if (argsNb < 2) { return "Invalid number of arguments";
			}else {
				return motorSmoothMove(cmdName.equals("left") ? true : false , args[0], args[1]);
			}
		} else if (cmdName.equals("left") || cmdName.equals("right")) {
			if (argsNb < 2) { return "Invalid number of arguments";
			}else {
				return motorMove(cmdName.equals("left") ? true : false , args[0], args[1]);
			}
		} else if (cmdName.equals("leftOld") || cmdName.equals("rightOld")) {
			if (argsNb < 2) { return "Invalid number of arguments";
			}else {
				return motorMoveOld(cmdName.equals("left") ? true : false , args[0], args[1]);
			}
		} else if (cmdName.equals("stop") or cmdName.equals("s")) {
			// stop motor
			return "Success";
		} else {
			return "Unknown command";
		}
	} else {
		return "Parsing error";
	}
}

String motorMoveOld(bool dir, int pulse, int d) {
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

String motorMove(bool dir, unsigned long degres, unsigned long durationForOneTurn) {
	// Enables the motor direction to move
	// LOW : left / HIGH : right
	// durationForOneTurn in s 
	// degres in degres
	fastDigitalWrite(_DIR_5v, dir ? LOW : HIGH); // setup dir
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

String motorSmoothMove(bool dir, unsigned long degres, unsigned long durationForOneTurn) {
	// like the previous ones but allow us to move forward more progressively.
	fastDigitalWrite(_DIR_5v, dir ? LOW : HIGH); // setup dir
	String r = "Success";
	unsigned long  microSecPerMotorTurn = (unsigned long)(1000000) * durationForOneTurn / _REDUCTION_RATIO;
	unsigned long demiStepDuration = microSecPerMotorTurn / _PULSE_PER_REV / 2;
	unsigned long pulseNb = (degres * _REDUCTION_RATIO * _PULSE_PER_REV) / 360;

	for(unsigned x = 0; x < pulseNb; x++) {
		float t = float(x)/float(pulseNb);
		float i = easeInOut(t);
		float iterpolatedDuration = float(demiStepDuration) * (1 + i);
		fastDigitalWrite(_STP_5v, HIGH);
		delayMicroseconds((unsigned long)(iterpolatedDuration));
		fastDigitalWrite(_STP_5v, LOW); 
		delayMicroseconds((unsigned long)(iterpolatedDuration));
		if(Serial.available()) { // break if incoming data in serial
			r = "Pulse:";
			r.concat(x+1);
			break;
		}
	}
	return r;
}

float easeInOut(float t) { 
	return t;
}

float interpolation(float t, float a, float b, float c, float d) {
	// t in [a, b]
	return c + easeInOut((t-a)/(b-a))*(d-c);
}

String blinkDebug() {
	digitalWrite(_debugLED, HIGH);
	delay(500);
	digitalWrite(_debugLED, LOW);
	return "Success";
}

void loop() {
	delay(1); // wait until receive Serial data
}
