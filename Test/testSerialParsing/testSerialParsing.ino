
# define _PULSE_PER_REV 800 // number of pulses for making one full cycle rotation
# define _REDUCTION_RATIO 6 // 10/60

# define _STP_5v 2 // PUL+(+5v) motor step control       White
# define _DIR_5v 3 // DIR+(+5v) motor direction control  Brown
# define _EN_5v  4 // ENA+(+5V) stepper motor enable     Yellow

const char* cmdDelimiter = ":";
const char* argumentDelimiter = ",";

const int serialbufferSize = 255;

char serialBuffer[serialbufferSize];   
int serialIndex = 0; // where we are in the buffer  

void setup() {
  //Sets the pins as Outputs
	for (int i = 8; i <= 13; i++) { // relai Outputs
		pinMode (i, OUTPUT);
		digitalWrite(i, LOW);
	}

	pinMode (_EN_5v, OUTPUT); // ENA+(+5V)
	pinMode (_DIR_5v, OUTPUT); // DIR+(+5v)
	pinMode (_STP_5v, OUTPUT); // PUL+(+5v)
	
  Serial.begin(115200); //enable Serial Monitor connection in 115200 baud to control from python7
  //Serial.println("start");
  // delay(10);
  // Serial.flush();
}

// char* concat(const char* s1, const char* s2){
//   char* result = malloc(strlen(s1) + strlen(s2) + 1);
//   strcpy(result, s1);
//   strcat(result, s2);
//   return result;
// }

boolean CheckSerial() {  
  boolean lineFound = false;  
  while (Serial.available() > 0) {  
    char charBuffer = (char)Serial.read();   
    if (charBuffer == '\n') { //end of line
          serialBuffer[serialIndex] = '\0'; // terminate the string  
          lineFound = (serialIndex > 0); // only good if we sent more than an empty line  
          serialIndex = 0; // reset for next line
    } else if(charBuffer == '\r') {  
      // Ignore the Carrage return, were only interested in new line  
    } else if(serialIndex < serialbufferSize && lineFound == false) {  
      serialBuffer[serialIndex++] = charBuffer; // auto increment index & add to our serialBuffer 
    }  
  }
  return lineFound;  
}

void setLedState(int ledNb, int state) {
  digitalWrite(7 + ledNb, (state == 1) ? HIGH : LOW);
}

int manualMove(bool dir, int pulse, int d) {
	// Enables the motor direction to move
	// LOW : left / HIGH : right
	digitalWrite(_DIR_5v, dir ? LOW : HIGH);

  long x = 0;
	for(; x < pulse; x++) {
		digitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(d);
		digitalWrite(_STP_5v, LOW); 
		delayMicroseconds(d);
		if(Serial.available()) { break; } // break if incoming data in serial
	}
	return x+1;
}

int motoMove(bool dir, long degres, long durationForOneTurn) {
	digitalWrite(_DIR_5v, dir == true ? LOW : HIGH); // setup dir
	long microSecPerMotorTurn = (long)1000000 * (long)durationForOneTurn / _REDUCTION_RATIO;
	long demiStepDuration = microSecPerMotorTurn / _PULSE_PER_REV / 2;
	long pulseNb = (long)degres * _REDUCTION_RATIO * _PULSE_PER_REV / 360;

  long x = 0;
	for(; x < pulseNb; x++) {
		digitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(demiStepDuration);
		digitalWrite(_STP_5v, LOW); 
		delayMicroseconds(demiStepDuration);
    if(Serial.available()) { break; } // break if incoming data in serial
	}
	return (x+1) * 360 / (_REDUCTION_RATIO * _PULSE_PER_REV);
}

int smoothMove(bool dir, bool inOut, long angle, long durationForOneTurn) {
	digitalWrite(_DIR_5v, dir == true ? LOW : HIGH); // setup dir
	long microSecPerMotorTurn = (long)1000000 * (long)durationForOneTurn / _REDUCTION_RATIO;
	long demiStepDuration = microSecPerMotorTurn / _PULSE_PER_REV / 2;
	long pulseNb = (long)angle * _REDUCTION_RATIO * _PULSE_PER_REV / 360;

  int inOutDirection = inOut ? 1 : -1;

  long x = 0;
	for(; x < pulseNb; x++) {
		float i = easeSigmoid((float)inOutDirection * (float(x)/float(pulseNb) - 0.5));
		float iterpolatedDuration = (float)demiStepDuration * (float)i;
		digitalWrite(_STP_5v, HIGH);
		delayMicroseconds(iterpolatedDuration);
		digitalWrite(_STP_5v, LOW); 
		delayMicroseconds(iterpolatedDuration);
    if(Serial.available()) { break; } // break if incoming data in serial
	}
  return (x+1) * 360 / (_REDUCTION_RATIO * _PULSE_PER_REV);
}

int captureMove(bool dir, long degres, long captureDegres, long durationForOneTurn) {
	digitalWrite(_DIR_5v, dir == true ? LOW : HIGH); // setup dir
	long microSecPerMotorTurn = (long)1000000 * (long)durationForOneTurn / _REDUCTION_RATIO;
	long demiStepDuration = microSecPerMotorTurn / _PULSE_PER_REV / 2;
	long pulseNb = (long)degres * _REDUCTION_RATIO * _PULSE_PER_REV / 360;
  long pulseCaptureNb = (long)captureDegres * _REDUCTION_RATIO * _PULSE_PER_REV / 360;

  long x = 0;
	for(; x < pulseNb; x++) {
		digitalWrite(_STP_5v, HIGH); 
		delayMicroseconds(demiStepDuration);
		digitalWrite(_STP_5v, LOW); 
		delayMicroseconds(demiStepDuration);
		if(x!= 0 && x%pulseCaptureNb == 0) {
			Serial.println("Capture");
		}
    if(Serial.available()) { break; } // break if incoming data in serial
	}
  Serial.println("Capture");
	return (x+1) * 360 / (_REDUCTION_RATIO * _PULSE_PER_REV);
}

int captureFull(bool dir, long degres, long captureDegres, long loadDegres, long durationForOneTurn) {
	int angleDone = 0;
	angleDone += smoothMove(dir, true, loadDegres, durationForOneTurn);
  if(Serial.available()) { return angleDone; }
	angleDone += captureMove(dir, degres, captureDegres, durationForOneTurn);
	if(Serial.available()) { return angleDone; }
	angleDone += smoothMove(dir, false, loadDegres, durationForOneTurn);
	if(Serial.available()) { return angleDone; }
	angleDone += smoothMove(!dir, true, loadDegres, durationForOneTurn);
	if(Serial.available()) { return angleDone; }
	angleDone += motoMove(!dir, degres, durationForOneTurn);
	if(Serial.available()) { return angleDone; }
	angleDone += smoothMove(!dir, false, loadDegres, durationForOneTurn);
	return angleDone;
}

float easeSigmoid(float t) {
	return 1.5 / (1.0 + exp(10.0 * t )) + 1.0;
}

String handleCmd(char* cmdBuffer) {
  char* cmdName = strtok(cmdBuffer, cmdDelimiter);
  
  if (!cmdName) {
    return "Error: parsing cmd error";
  }

  char* arg0 = strtok(NULL, argumentDelimiter);
  char* arg1 = strtok(NULL, argumentDelimiter);
  char* arg2 = strtok(NULL, argumentDelimiter);
  char* arg3 = strtok(NULL, argumentDelimiter);
  char* arg4 = strtok(NULL, argumentDelimiter);
  
  if (strncmp(cmdBuffer, "led", 3) == 0) {
		if (arg0 == NULL || arg1 == NULL) { 
			return "Error: invalid number of arguments (led number[1, 6] & state(0 or 1) needed)";
		}
    int ledNb = atoi(arg0);
    if(ledNb < 1 || ledNb > 6) {
      return "Error: invalid led number (must be in [1, 6])";
    }
    int state = atoi(arg1);

    setLedState(ledNb, state);
    return "Success: led " + String(ledNb) + (state ? "on": "off");

  } else if (strncmp(cmdBuffer, "stop", 4) == 0) {
		return "Success: motor stop";

  }else {
    if(arg0 == NULL) {
      return "Error: invalid first argument direction must be 1 for left or 0 for right";
    }
    int dir = atoi(arg0);

    if (strncmp(cmdBuffer, "captureFull", 11) == 0) {
      if (arg1 == NULL || arg2 == NULL || arg3 == NULL || arg4 == NULL) {
			  return "Error: invalid number of arguments (angle(deg), captureAngle(deg), smoothAngle(deg) & durationForOneTurn(sec/tr) needed)";
      }
      int angle = atoi(arg1);
      int captureAngle = atoi(arg2);
      int smoothAngle = atoi(arg3);
      int durationForOneTurn = atoi(arg4);

      // Serial.print("Error :");
      // Serial.print(angle);
      // Serial.print("-");
      // Serial.print(captureAngle);
      // Serial.print("-");
      // Serial.print(smoothAngle);
      // Serial.print("-");
      // Serial.println(durationForOneTurn);

      int angleDone = captureFull(dir, angle, captureAngle, smoothAngle, durationForOneTurn);
      if( angleDone == angle) {
        return "Success : motor movement done";
      }else {
        return "Error: angleDone(" + String(angleDone) + "/" + String(2* angle + 4 * smoothAngle) + ")";
      } 

    }else if (strncmp(cmdBuffer, "capture", 7) == 0) {
      if (arg1 == NULL || arg2 == NULL || arg3 == NULL || arg4 == NULL) { 
			  return "Error: invalid number of arguments (angle(deg), captureAngle(deg), smoothAngle(deg) & durationForOneTurn(sec/tr) needed)";
      }
      int angle = atoi(arg1);
      int captureAngle = atoi(arg2);
      int smoothAngle = atoi(arg3);
      int durationForOneTurn = atoi(arg4);

      int angleDone = captureMove(dir, angle, captureAngle, durationForOneTurn);
      if( angleDone == angle) {
        return "Success : motor movement done";
      }else {
        return "Error: angleDone(" + String(angleDone) + "/" + String(angle) + ")";
      }

    }else if (strncmp(cmdBuffer, "smooth", 6) == 0) {
      if (arg1 == NULL || arg2 == NULL || arg3 == NULL) {
			  	return "Error: invalid number of arguments easing direction(0 or 1), angle(deg) & durationForOneTurn(sec/tr) needed)";
      }
      int easeDir = atoi(arg1);
      int angle = atoi(arg2);
      int durationForOneTurn = atoi(arg3);

      int angleDone = smoothMove(dir, easeDir, angle, durationForOneTurn);
      if( angleDone == angle) {
        return "Success : motor movement done";
      }else {
        return "Error: angleDone(" + String(angleDone) + "/" + String(angle) + ")";
      }

    }else if (strncmp(cmdBuffer, "move", 4) == 0) {
      if (arg1 == NULL || arg2 == NULL) {
			  	return "Error: invalid number of arguments , angle(deg) & durationForOneTurn(sec/tr) needed)";
      }
      int angle = atoi(arg1);
      int durationForOneTurn = atoi(arg2);

      int angleDone = motoMove(dir, angle, durationForOneTurn);
      if( angleDone == angle) {
        return "Success : motor movement done";
      }else {
        return "Error: angleDone(" + String(angleDone) + "/" + String(angle) + ")";
      }

    }else if (strncmp(cmdBuffer, "manual", 6) == 0) {
      if (arg1 == NULL || arg2 == NULL) {
			  	return "Error: invalid number of arguments (pulseNumber & pulseDelay needed)";
      }
      int pulseNumber = atoi(arg1);
      int pulseDelay = atoi(arg2);

      int pulseDone = manualMove(dir, pulseNumber,pulseDelay);
      if( pulseDone == pulseNumber) {
        return "Success : motor movement done";
      }else {
        return "Error: pulseDone(" + String(pulseDone) + "/" + String(pulseNumber) + ")";
      }

    }else {
      return "Error: Unknown command \"" + String(cmdName) + "\"";
    }
  }
}

void loop() {
  if (CheckSerial()) {
    Serial.println(handleCmd(serialBuffer));   
  }
  delay(1);
}
