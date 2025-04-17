// PWM pinnen voor aansturing kleppen
int PWM_ven = 9;
int PWM_art = 11;

// Stabiele situatie
float dc_art_stabiel = 95;
float dc_ven_stabiel = 90;
byte PWM_art_stabiel = 255 * dc_art_stabiel / 100;
byte PWM_ven_stabiel = 255 * dc_ven_stabiel / 100;

String scenarios = "[occlusie_art-mild]/[occlusie_art-ernstig]/[occlusie_ven-mild]/[occlusie_ven-ernstig]/[hypotensie]/[hypertensie]/[stabiel]";

void setup() {
  Serial.begin(9600);
  pinMode(PWM_ven, OUTPUT);
  pinMode(PWM_art, OUTPUT);

  analogWrite(PWM_ven, PWM_ven_stabiel);
  analogWrite(PWM_art, PWM_art_stabiel);

  delay(2000);
  Serial.println("Welkom bij het scenarioprogramma. Mogelijke scenario’s:");
  Serial.println(" - [Hypertensie]\n - [Hypotensie]");
  Serial.println(" - Arteriële occlusie: [occlusie_art-mild] / [occlusie_art-ernstig]");
  Serial.println(" - Veneuze occlusie: [occlusie_ven-mild] / [occlusie_ven-ernstig]");
  Serial.println(" - Terug naar stabiel: [stabiel]");
}

void setPWM(float dc_art, float dc_ven, String msg) {
  Serial.println(msg);
  analogWrite(PWM_art, byte(dc_art / 100 * 255));
  analogWrite(PWM_ven, byte(dc_ven / 100 * 255));
  Serial.println("READY");
}

void simulateScenario(float dc_art, float dc_ven, int duration_ms, int steps) {
  float start_art = analogRead(PWM_art) / 255.0 * 100;
  float start_ven = analogRead(PWM_ven) / 255.0 * 100;
  float step_art = (dc_art - start_art) / steps;
  float step_ven = (dc_ven - start_ven) / steps;

  for (int i = 0; i <= steps; i++) {
    float new_art = start_art + i * step_art;
    float new_ven = start_ven + i * step_ven;
    analogWrite(PWM_art, byte(new_art / 100 * 255));
    analogWrite(PWM_ven, byte(new_ven / 100 * 255));
    delay(duration_ms / steps);
  }

  Serial.println("READY");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    Serial.println(command);

    if (command.equalsIgnoreCase("hypertensie")) {
      simulateScenario(70, 90, 30000, 10);

    } else if (command.equalsIgnoreCase("hypotensie")) {
      simulateScenario(95, 62, 30000, 10);

    } else if (command.equalsIgnoreCase("occlusie_art-mild")) {
      setPWM(69, 90, "Scenario milde arteriële occlusie start");

    } else if (command.equalsIgnoreCase("occlusie_art-ernstig")) {
      setPWM(66, 90, "Scenario ernstige arteriële occlusie start");

    } else if (command.equalsIgnoreCase("occlusie_ven-mild")) {
      setPWM(95, 60, "Scenario milde veneuze occlusie start");

    } else if (command.equalsIgnoreCase("occlusie_ven-ernstig")) {
      setPWM(95, 58, "Scenario ernstige veneuze occlusie start");

    } else if (command.equalsIgnoreCase("stabiel")) {
      setPWM(dc_art_stabiel, dc_ven_stabiel, "Terug naar de stabiele situatie");

    } else if (command.startsWith("DC-Arterieel")) {
      int art_index = command.indexOf("DC-Arterieel-") + 13;
      int ven_index = command.indexOf("-Veneus-");
      float art = command.substring(art_index, ven_index).toFloat();
      float ven = command.substring(ven_index + 8).toFloat();
      setPWM(art, ven, "Handmatige aanpassing uitgevoerd");

    } else {
      Serial.println("Ongeldig scenario. Kies uit:");
      Serial.println(scenarios);
    }
  }
}
