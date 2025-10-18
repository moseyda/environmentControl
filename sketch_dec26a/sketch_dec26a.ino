#include <DHT.h>            // Include library for DHT sensors
#include <LiquidCrystal.h>  // Include library for LCD

// Initialize the LCD by specifying its connected pins
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Define the pin and type for the DHT sensor
#define DHTPIN 7  // DHT sensor connected to pin 7
#define DHTTYPE DHT11  // Specify the sensor type (DHT11)

// Create a DHT object
DHT dht(DHTPIN, DHTTYPE);

// Define LED pins
int greenLedPin = 9;  // Pin for green LED (too low temperature)
int redLedPin = 10;   // Pin for red LED (too high temperature)

// Define temperature thresholds
float tempHighThreshold = 30.0;  // Example: 30°C is too high
float tempLowThreshold = 12.0;   // Example: 18°C is too low

// Define MQ-135 sensor pin
int mq135Pin = A0;  // MQ-135 sensor connected to A0

void setup() {
  lcd.begin(16, 2);      // Start the LCD with 16 columns and 2 rows
  lcd.print("Env Monitoring");
  delay(2000);           // Delay for 2 seconds
  lcd.clear();           // Clear the LCD screen after delay
  Serial.begin(9600);    // Start serial communication for debugging

  // Initialize the DHT sensor
  dht.begin();

  // Initialize LED pins as outputs
  pinMode(redLedPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);

  // Turn off LEDs initially
  digitalWrite(redLedPin, LOW);
  digitalWrite(greenLedPin, LOW);
}

void loop() {
  // -------- Read Temperature and Humidity from DHT11 --------
  float temperatureC = dht.readTemperature();  // Read temperature in Celsius
  float humidity = dht.readHumidity();         // Read humidity in percentage

  // Check if the readings are valid
  if (isnan(temperatureC) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("DHT Error!");
    delay(2000);  // Wait for 2 seconds and retry
    return;
  }

  // -------- Read Air Quality from MQ-135 --------
  int mq135Value = analogRead(mq135Pin);  // Read the analog value from MQ-135
  float airQuality = map(mq135Value, 0, 1023, 0, 100);  // Map the value to a percentage (0-100)

  // -------- LED Control Based on Temperature --------
  if (temperatureC > tempHighThreshold) {
    // Temperature is too high: Turn on red LED, turn off green LED
    digitalWrite(redLedPin, HIGH);
    digitalWrite(greenLedPin, LOW);
  } else if (temperatureC < tempLowThreshold) {
    // Temperature is too low: Turn on green LED, turn off red LED
    digitalWrite(redLedPin, LOW);
    digitalWrite(greenLedPin, HIGH);
  } else {
    // Temperature is within normal range (18°C - 30°C): Turn off both LEDs
    digitalWrite(redLedPin, HIGH);
    digitalWrite(greenLedPin, HIGH);
  }

  // -------- Display temperature --------
  lcd.clear();  // Clear the LCD to avoid overlapping text
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temperatureC);
  lcd.print(" C");

  // -------- Display humidity --------
  lcd.setCursor(0, 1);
  lcd.print("Humidity: ");
  lcd.print(humidity);
  lcd.print("%");

  delay(3000);  // Wait for 3 seconds and clear the LCD

  // -------- Display air quality --------
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Air Quality: ");
  lcd.print(airQuality);
  lcd.print("%");

  delay(3000);  // Wait for another 3 seconds before updating again

  // -------- Serial Monitor for Debugging --------
  Serial.print("Temp: ");
  Serial.print(temperatureC);
  Serial.print(" C | Humidity: ");
  Serial.print(humidity);
  Serial.print("% | Air Quality: ");
  Serial.println(airQuality);
}
