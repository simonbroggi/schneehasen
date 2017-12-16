#define RELAY1  2  
#define RELAY2  3  
#define RELAY3  4  
#define RELAY4  5  
#define RELAY5  6  
#define RELAY6  7  
#define RELAY7  8  
#define RELAY8  9  

#define ON   LOW  
#define OFF  HIGH  

unsigned long lastLoopTime = 0UL;

byte relais[] = { RELAY1, RELAY2, RELAY3, RELAY4, RELAY5, RELAY6, RELAY7, RELAY8, 10, 11 };
const byte numRelais = sizeof(relais) / sizeof(byte);

byte onPos[] = { 0, 4 };
const byte numOnPos = sizeof(onPos) / sizeof(byte);
unsigned long onPosMoveT[numOnPos];
unsigned long onPosMoveDelay[numOnPos];

void setup() {
  randomSeed(analogRead(0));
//  delay(5000);
//  Serial.print("hello world\n");
  for (int i = 0; i < numRelais; i++) {
    pinMode(relais[i], OUTPUT);
  }
  for (int i = 0; i < numOnPos; i++) {
    onPosMoveDelay[i] = 500000;
    onPosMoveT[i] = onPosMoveDelay[i];
  }
  onPosMoveDelay[1] = 400000;
//  printOnPosMoveT();
//  printOnPosMoveDelay();
//  Serial.print("ok?\n");
  setRelaisStates();

  
}

void loop() {
  //calculate dt: delta time since last loop
  unsigned long currentLoopTime = micros();
  if(currentLoopTime < lastLoopTime) { //check time overflow
    lastLoopTime = 0UL;
  }
  unsigned long dt = currentLoopTime - lastLoopTime;
  lastLoopTime = currentLoopTime;
  
//  String dtDebug = "dt:";
//  dtDebug = dtDebug + dt + "\n";
//  Serial.print(dtDebug);
  if (updateOnPos(dt)) {
    setRelaisStates();
  } 
//  printOnPosMoveT();
//  printOnPosMoveDelay();
}

bool updateOnPos(unsigned long dt) {
  bool change = false;
  for(int i=0; i < numOnPos; i++) {
    if(onPosMoveT[i] <= dt) {
      onPosMoveT[i] = onPosMoveDelay[i] + random(-50000, 50000);
      onPos[i] = (onPos[i] + 1) % numRelais;
      change = true;
    }
    else {
      onPosMoveT[i] -= dt;
    }
  }
  return change;
}

void printOnPosMoveT() {
  String onPosMoveTDebug = "onPosMoveTDebug:  ";
  for(int i=0; i < numOnPos; i++) {
    onPosMoveTDebug += onPosMoveT[i];
    onPosMoveTDebug += "    ";
  }
  onPosMoveTDebug += "\n";
  Serial.print(onPosMoveTDebug);
}

void printOnPosMoveDelay() {
  String onPosMoveDelayDebug = "onPosMoveDelayDebug:  ";
  for(int i=0; i < numOnPos; i++) {
    onPosMoveDelayDebug += onPosMoveDelay[i];
    onPosMoveDelayDebug += "    ";
  }
  onPosMoveDelayDebug += "\n";
  Serial.print(onPosMoveDelayDebug);
}

void setRelaisStates() {
  bool relaisOn[numRelais];
  for(int i=0; i < numRelais; i++) {
    relaisOn[i] = false;
  }
  for(int i=0; i < numOnPos; i++) {
    relaisOn[onPos[i]] = true;
  }
  for(int i=0; i < numRelais; i++) {
    digitalWrite(relais[i], relaisOn[i]?ON:OFF);
  }
}
