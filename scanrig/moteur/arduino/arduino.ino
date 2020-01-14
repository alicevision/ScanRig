// ENA-(ENA) stepper motor enable, connected to ground
// DIR-(DIR) motor direction control, connected to ground
// PUL-(PUL) motor step control, connected to ground

# define _MAX_ARG 10
# define _PULSE_PER_REV 200 // number of pulses for making one full cycle rotation
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
			bufferStr = ""; // reset command incoming buffer
		} else {
			bufferStr += inChar;
		}
	}
}

void handleReceivedCommand(String str) {
	// format 
	// cmd:arg01,arg02, ...
	Serial.println("recieved cmd : \"" + str + "\"");

	int id;

	String cmdName;
	int argsBuffer[_MAX_ARG];
	// memset(argsBuffer, 0, sizeof(argsBuffer));

	id = str.indexOf(':');

	if(id != -1) {
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

		if (cmdName.equals("right")) { // equalsIgnoreCase
			blinkDebug(); wait(100); blinkDebug();
		} else if (cmdName.equals("left")) {
			blinkDebug();
		} else {
			Serial.println("Cmd received: unknown");
		}

		

	}else {
		Serial.println("cmd not found, parsing error");
		return;
	}
}

void motorMove(bool dir, unsigned int pulse) {
	// Enables the motor direction to move
	fastDigitalWrite(_DIR_5v, dir ? HIGH : LOW);

	// Makes 200 Pulses for making one full cycle rotation
	
	// float pulse = _PULSE_PER_REV/360.0f*float(angle);
	// Serial.println("pulse : " + pulse);
	for(int x = 0; x < pulse; x++) {
		fastDigitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(500); 
		fastDigitalWrite(_STP_5v, LOW); 
		delayMicroseconds(500); 
	}
}

void blinkDebug() {
	digitalWrite(_debugLED, HIGH);
	delayMicroseconds(100); // 100 ms
	digitalWrite(_debugLED, LOW);
}

void loop() {
	// test loop
	motorMove(true, 400);
	delay(1000);
	motorMove(false, 200);
	delay(500);
}
