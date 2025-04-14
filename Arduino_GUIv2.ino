// Definiëring van de PWM pins
int PWM_ven = 9;
int PWM_art = 11;

// Definiëring van de stabiele duty cycles en bijbehorende bytewaarde
float dc_art_stabiel = 95;
float dc_ven_stabiel = 90;
byte PWM_art_stabiel = 255 * dc_art_stabiel / 100;
byte PWM_ven_stabiel = 255 * dc_ven_stabiel / 100;
String klaar = "Het scenario is afgespeeld. Type zodra je er klaar voor bent [stabiel] om terug te keren naar de stabiele situatie";
String scenarios = "[occlusie_art]/[occlusie_ven]/[hypotensie]/[hypertensie]/[stabiel]";

void setup() {
  // Open een seriële monitor met 9600 baudes.
  Serial.begin(9600);

  // Initialiseer de uitgangspinnen
  pinMode(PWM_ven, OUTPUT);
  pinMode(PWM_art, OUTPUT);

  // Stel de beginwaarden in
  analogWrite(PWM_ven, PWM_ven_stabiel);  // veneus
  analogWrite(PWM_art, PWM_art_stabiel);  // arterieel

  // Stel de frequentie voor PWM in (1 kHz voor pinnen 9 en 11)
  setupPWMFrequency();

  delay(2000);
  Serial.println("Welkom bij scenarioprogramma. Speel één van de volgende scenario's af. Type na een scenario stabiel om terug te gaan naar de stabiele situatie");
  Serial.println(" - [Hypertensie]");
  Serial.println(" - [Hypotensie]");
  Serial.println(" - Een milde of ernstige arteriële occlusie --> [occlusie_art]");
  Serial.println(" - Een milde of ernstige veneuze occlusie --> [occlusie_ven]");
  Serial.println(" - Een stabiele patiënt aan de ECMO --> [stabiel]");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readString();
    command.trim();

    // Verwerken van de ontvangen duty cycle waarden
    if (command.startsWith("DC-Arterieel-") && command.indexOf("Veneus-") != -1) {
      int art_dc_start = command.indexOf("DC-Arterieel-") + 13;
      int ven_dc_start = command.indexOf("Veneus-") + 7;
      
      String art_dc_str = command.substring(art_dc_start, command.indexOf("-", art_dc_start));
      String ven_dc_str = command.substring(ven_dc_start);

      int art_dc = art_dc_str.toInt();
      int ven_dc = ven_dc_str.toInt();
      
      // Pas de duty cycles aan
      byte PWM_art = map(art_dc, 55, 95, 0, 255);  // Arterieel
      byte PWM_ven = map(ven_dc, 55, 95, 0, 255);  // Veneus

      analogWrite(PWM_ven, PWM_ven);  // Pas de duty cycle aan voor veneus
      analogWrite(PWM_art, PWM_art);  // Pas de duty cycle aan voor arterieel

      Serial.println("Duty cycle waarden zijn bijgewerkt.");
    }

    // Scenario Afhandeling
    else if (command.equalsIgnoreCase("hypertensie") || command.equalsIgnoreCase("[hypertensie]")) {
      // Scenario hypertensie begin
      Serial.println("Scenario hypertensie begint.");
      analogWrite(PWM_ven, map(95, 55, 95, 0, 255));  // Voorbeeld waarde voor veneus
      analogWrite(PWM_art, map(70, 55, 95, 0, 255));  // Voorbeeld waarde voor arterieel
      Serial.println(klaar);
    }

    else if (command.equalsIgnoreCase("stabiel") || command.equalsIgnoreCase("[stabiel]")) {
      Serial.println("Terug naar stabiele situatie.");
      analogWrite(PWM_ven, PWM_ven_stabiel);  // Stabiele waarde voor veneus
      analogWrite(PWM_art, PWM_art_stabiel);  // Stabiele waarde voor arterieel
      Serial.println(klaar);
    }

    // Voeg andere scenario's toe (zoals occlusie) indien nodig.
  }
}

// Functie om de PWM-frequentie in te stellen op 1 kHz voor pinnen 9 en 11
void setupPWMFrequency() {
  // We passen de timerinstellingen aan voor pinnen 9, 10 (Timer1) en 11 (Timer2)

  // Stop Timer1 voordat we de instellingen wijzigen
  TCCR1A = 0;
  TCCR1B = 0;

  // Stel Timer1 in voor een prescaler van 8, wat een frequentie van 1 kHz oplevert voor pinnen 9 en 10
  TCCR1B |= (1 << WGM12); // CTC mode (Clear Timer on Compare Match)
  TCCR1B |= (1 << CS11);  // Prescaler van 8
  OCR1A = 1999;  // (16 MHz / 8 / 2000) = 1 kHz

  // Stop Timer2 voordat we de instellingen wijzigen (voor pin 11)
  TCCR2A = 0;
  TCCR2B = 0;

  // Stel Timer2 in voor een prescaler van 8, wat een frequentie van 1 kHz oplevert voor pin 11
  TCCR2B |= (1 << WGM21); // CTC mode (Clear Timer on Compare Match)
  TCCR2B |= (1 << CS21);  // Prescaler van 8
  OCR2A = 1999;  // (16 MHz / 8 / 2000) = 1 kHz
}
