int flashPin = 12;

void setup() {
  Serial.begin(9600);

  // setup output flashPin
  pinMode(flashPin, OUTPUT);
  digitalWrite(flashPin, LOW);
}

void flash(int d) {
  digitalWrite(flashPin, HIGH);
  delay(d);
  digitalWrite(flashPin, LOW);
}

void loop() {
  if ( Serial.available() ) {
    int str = Serial.read();
    if (str == 102 or str == 112) { // 102 for f or p
      flash(10);
    }else if (str != 10) { // for \n
      Serial.println(str);
    }
  }
  delay(1);
}
