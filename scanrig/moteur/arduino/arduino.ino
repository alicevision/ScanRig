// ENA-(ENA) stepper motor enable, connected to ground
// DIR-(DIR) motor direction control, connected to ground
// PUL-(PUL) motor step control, connected to ground

# define _MAX_ARG 10
# define _PULSE_PER_REV 200 // number of pulses for making one full cycle rotation
# define _EN_5v  4 // ENA+(+5V) stepper motor enable     White
# define _DIR_5v 3 // DIR+(+5v) motor direction control  Brown
# define _STP_5v 2 // PUL+(+5v) motor step control       Yellow

# define _debugLED 13 // debug led

int speed = 500;

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

// advenced digitalWrite function
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
			handleReceivedCommand(bufferStr);
			bufferStr = ""; // reset command incoming buffer (allow us to break motor during rotation)
		} else {
			bufferStr += inChar;
		}
	}
}

void handleReceivedCommand(String str) {

	// command format	cmd:arg01,arg02, ...

	// Serial.println("recieved cmd : \"" + str + "\"");

	int id;

	String cmdName;
	int argsBuffer[_MAX_ARG];
	// memset(argsBuffer, 0, sizeof(argsBuffer));

	id = str.indexOf(':');
	if (id != -1) {
		cmdName = str.substring(0, id);
		str = str.substring(id+1);
		
		int argsNb = 0;
		while ( (id = str.indexOf(',') ) != -1 && argsNb < _MAX_ARG) { // for each args passed
			argsBuffer[argsNb] = str.substring(0, id).toInt();
			str = str.substring(id+1);
			argsNb++;
		}
		// read last arg if needed (because of stop condition in while)
		if (argsNb < _MAX_ARG) {
			argsBuffer[argsNb] = str.substring(0, id).toInt();
		}

		int args[argsNb+1];
		memcpy(args, argsBuffer, sizeof(args)); // copy argsbuffer array to args array
		
		Serial.println("cmd : " + cmdName);

		// ============================================================
		// ======================== commands ==========================
		// ============================================================

		if (cmdName.equals("debugBlink")) { // equalsIgnoreCase
			blinkDebug(); delay(500); blinkDebug();
		} else if (cmdName.equals("left")) {
			if (argsNb < 0) {
				Serial.println("invalid nb of arguments");
			}else {
				motorMove(true, args[0]);
			}
		} else if (cmdName.equals("right")) {
			if (argsNb < 0) {
				Serial.println("invalid nb of arguments");
			}else {
				motorMove(false, args[0]);
			}
		} else if (cmdName.equals("speed")) {
			if (argsNb < 0) {
				Serial.println("invalid nb of arguments");
			}else {
				speed = args[0];
			}
		} else if (cmdName.equals("test")) {
			if (argsNb < 1) {
				Serial.println("invalid nb of arguments");
			} else {
				testTimeMotor(args[0], args[1]);
			}
		} else if (cmdName.equals("stop") or cmdName.equals(" ")) {
			// stop motor
		} else {
			Serial.println("Unknown Cmd");
		}
	} else {
		if(!str.equals(" ")) {
			Serial.println("Parsing error :\"" + str + "\"");
		}// else {
		 // 	// motorStop
		 // }
	}
}

void testTimeMotor(unsigned int d, unsigned int pulse) {
	fastDigitalWrite(_DIR_5v,HIGH);
	
	for(int x = 0; x < pulse; x++) {
		fastDigitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(d); 
		fastDigitalWrite(_STP_5v, LOW); 
		delayMicroseconds(d);
		if(Serial.available()) {
			break;
		}
	}
}

void motorMove(bool dir, unsigned int pulse) {
	// Enables the motor direction to move
	// LOW : left / HIGH : right
	fastDigitalWrite(_DIR_5v, dir ? LOW : HIGH);
	
	for(int x = 0; x < pulse; x++) {
		fastDigitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(speed); 
		fastDigitalWrite(_STP_5v, LOW); 
		delayMicroseconds(speed);
		if(Serial.available()) { // break if incoming data in serial
			break;
		}
	}
}

void blinkDebug() {
	digitalWrite(_debugLED, HIGH);
	delay(500); // 100 ms
	digitalWrite(_debugLED, LOW);
}

void loop() {
	// test loop
	// motorMove(true, 400);
	// delay(1000);
	// motorMove(false, 400);
	// delay(1000);
}
