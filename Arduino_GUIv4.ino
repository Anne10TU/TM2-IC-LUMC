// Definieer de PWM-pinnen
int PWM_ven = 9;
int PWM_art = 11;



// Stabiele situatie
float dc_art_stabiel = 95;
float dc_ven_stabiel = 90;
byte PWM_art_stabiel = 255 * dc_art_stabiel / 100;
byte PWM_ven_stabiel = 255 * dc_ven_stabiel / 100;

String klaar = "Het scenario is afgespeeld. Type zodra je er klaar voor bent [stabiel] om terug te keren naar de stabiele situatie";
String scenarios = "[occlusie_art]/[occlusie_ven]/[hypotensie]/[hypertensie]/[stabiel]";

void setup() {
  Serial.begin(9600);
  pinMode(PWM_ven, OUTPUT);
  pinMode(PWM_art, OUTPUT);
  //setupPWMFrequency();

  // Start in stabiele toestand
  analogWrite(PWM_ven, PWM_ven_stabiel);
  analogWrite(PWM_art, PWM_art_stabiel);

  delay(2000);
  Serial.println("Welkom bij het scenarioprogramma. Mogelijke scenario’s:");
  Serial.println(" - [Hypertensie]\n - [Hypotensie]");
  Serial.println(" - Arteriële occlusie: [occlusie_art]");
  Serial.println(" - Veneuze occlusie: [occlusie_ven]");
  Serial.println(" - Terug naar stabiel: [stabiel]");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readString();
    command.trim();
    Serial.println(command);

    if (command.equalsIgnoreCase("hypertensie") || command.equalsIgnoreCase("[hypertensie]")) {
      Serial.println("Scenario hypertensie begint.");
      simulateScenario(70, 90, 30000, 10);  // Arterieel daalt, veneus blijft stabiel

    } else if (command.equalsIgnoreCase("hypotensie") || command.equalsIgnoreCase("[hypotensie]")) {
      Serial.println("Scenario hypotensie begint.");
      Serial.println("READY");
      simulateScenario(95, 62, 30000, 10);  // Arterieel stabiel, veneus daalt

    } else if (command.equalsIgnoreCase("occlusie_art") || command.equalsIgnoreCase("[occlusie_art]")) {
      Serial.println("Hoe erg is de occlusie? Kies uit: [mild] of [ernstig]");
      waitForInput();
      String ernst = Serial.readString();
      ernst.trim();

      if (ernst.equalsIgnoreCase("mild")) {
        setPWM(69, 90, "Scenario milde arteriële occlusie start");
      } else if (ernst.equalsIgnoreCase("ernstig")) {
        setPWM(66, 90, "Scenario ernstige arteriële occlusie start");
      } else {
        Serial.println("Ongeldige keuze. Kies opnieuw een scenario:");
        Serial.println(scenarios);
      }

    } else if (command.equalsIgnoreCase("occlusie_ven") || command.equalsIgnoreCase("[occlusie_ven]")) {
      Serial.println("Hoe erg is de occlusie? Kies uit: [mild] of [ernstig]");
      waitForInput();
      String ernst = Serial.readString();
      ernst.trim();

      if (ernst.equalsIgnoreCase("mild")) {
        setPWM(95, 60, "Scenario milde veneuze occlusie start");
      } else if (ernst.equalsIgnoreCase("ernstig")) {
        setPWM(95, 58, "Scenario ernstige veneuze occlusie start");
      } else {
        Serial.println("Ongeldige keuze. Kies opnieuw een scenario:");
        Serial.println(scenarios);
      }

    } else if (command.equalsIgnoreCase("stabiel") || command.equalsIgnoreCase("[stabiel]")) {
      setPWM(dc_art_stabiel, dc_ven_stabiel, "Terug naar de stabiele situatie");

    } else {
      Serial.println("Ongeldig scenario. Kies uit:");
      Serial.println(scenarios);
    }
  }
}

// Simuleert een scenario met geleidelijke verandering
void simulateScenario(float dc_art_doel, float dc_ven_doel, int totaalTijd, int stappen) {
  float delta_art = dc_art_doel - dc_art_stabiel;
  float delta_ven = dc_ven_doel - dc_ven_stabiel;

  for (int i = 1; i <= stappen; i++) {
    float dc_art_now = dc_art_stabiel + (delta_art / stappen * i);
    float dc_ven_now = dc_ven_stabiel + (delta_ven / stappen * i);
    analogWrite(PWM_art, dc_art_now * 255 / 100);
    analogWrite(PWM_ven, dc_ven_now * 255 / 100);
    delay(totaalTijd / stappen);

    // Feedback naar de Raspberry Pi sturen
    Serial.print("PWM Art: ");
    Serial.print(dc_art_now);
    Serial.print(", PWM Ven: ");
    Serial.println(dc_ven_now);
  }
  Serial.println(klaar);
}

// Zet meteen nieuwe PWM waarden voor een scenario
void setPWM(float dc_art, float dc_ven, String message) {
  Serial.println(message);
  byte pwm_art = dc_art * 255 / 100;
  byte pwm_ven = dc_ven * 255 / 100;
  analogWrite(PWM_art, pwm_art);
  analogWrite(PWM_ven, pwm_ven);
  delay(1000);

  // Feedback naar de Raspberry Pi sturen
  Serial.print("Nieuwe PWM Art: ");
  Serial.print(dc_art);
  Serial.print(", Nieuwe PWM Ven: ");
  Serial.println(dc_ven);

  Serial.println(klaar);
}

// Wacht totdat gebruiker iets typt
void waitForInput() {
  while (!Serial.available()) {
    delay(100);
  }
}

// PWM-frequentie instellen (voor pin 9 en 11)
//void setupPWMFrequency() {
  // Timer1 voor pin 9 (Arduino Uno)
  //TCCR1B = TCCR1B & 0b11111000 | 0x01; // 31 kHz

  // Timer2 voor pin 11 (Arduino Uno)
  //TCCR2B = TCCR2B & 0b11111000 | 0x01; // 31 kHz
//}
