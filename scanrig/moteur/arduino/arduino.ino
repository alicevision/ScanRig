// ENA-(ENA) stepper motor enable, connected to ground
// DIR-(DIR) motor direction control, connected to ground
// PUL-(PUL) motor step control, connected to ground

# define _MAX_ARG 10
# define _PULSE_PER_REV 200 // number of pulses for making one full cycle rotation
# define _EN_5v  4 // ENA+(+5V) stepper motor enable     White
# define _DIR_5v 3 // DIR+(+5v) motor direction control  Brown
# define _STP_5v 2 // PUL+(+5v) motor step control       Yellow

# define _debugLED 13 // debug led

int pulseDelay;

void setup() {
	//Sets the pins as Outputs
	pinMode (_debugLED, OUTPUT); // debug led already on arduino
	pinMode (_EN_5v, OUTPUT); // ENA+(+5V)
	pinMode (_DIR_5v, OUTPUT); // DIR+(+5v)
	pinMode (_STP_5v, OUTPUT); // PUL+(+5v)
	
	//enable Serial Monitor connection in 115200 baud to control from python
	Serial.begin(115200);
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
		} else if (cmdName.equals("left") || cmdName.equals("right")) {
			if(argsNb == 1) {
				return motorMove(cmdName.equals("left") ? true : false , args[0], pulseDelay);
			}else if(argsNb == 2) {
				return motorMove(cmdName.equals("left") ? true : false , args[0], args[1]);
			}else {
				return "Invalid number of arguments";
			}
		} else if (cmdName.equals("setPulseDelay")) {
			if (argsNb <= 0) { return "Invalid number of arguments";
			}else {
				pulseDelay = args[0];
				return "Success";
			}
		} else if (cmdName.equals("test")) {
			return testMotor();
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


String motorMove(bool dir, int pulse, int delay) {
	// Enables the motor direction to move
	// LOW : left / HIGH : right
	fastDigitalWrite(_DIR_5v, dir ? LOW : HIGH);
	String r = "Success";
	
	for(int x = 0; x < pulse; x++) {
		fastDigitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(delay); 
		fastDigitalWrite(_STP_5v, LOW); 
		delayMicroseconds(delay);
		
		if(Serial.available()) { // break if incoming data in serial
			r = "Pulse:";
			r.concat(x+1);
			break;
		}
	}
	return r;
}


String testMotor() {
	String rtn;
	rtn = motorMove(true, 320, pulseDelay);
	if (rtn.equals("Success") == false) { return rtn; }; // return error if not success
	delay(500);
	rtn = motorMove(true, 320, pulseDelay);
	if (rtn.equals("Success") == false) { return rtn; };
	delay(500);
	rtn = motorMove(true, 320, pulseDelay);
	if (rtn.equals("Success") == false) { return rtn; };
	delay(500);
	rtn = motorMove(true, 320, pulseDelay);
	if (rtn.equals("Success") == false) { return rtn; };
	delay(500);
	rtn = motorMove(true, 320, pulseDelay);
	if (rtn.equals("Success") == false) { return rtn; };
	delay(1000);
	rtn = motorMove(false, 1600, pulseDelay);
	if (rtn.equals("Success") == false) { return rtn; };
	return "Success";
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
