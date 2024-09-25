# Interactive-Game-Control-System
# Interactive-Game-Control-System
Project Title
Interactive Game with Arduino, Joystick, and Ultrasonic Sensor

DESCRIPTION

This project is an interactive game developed in Python using the Pygame library. The player controls an on-screen character via a joystick connected to an Arduino. The game also integrates an ultrasonic sensor that adds a "protective shield" mechanic when the player's hand approaches the sensor. Additionally, the player can shoot projectiles by pressing the joystick button to eliminate enemies on the screen.

MAIN FEATURES

- Character Control: Smooth character movement using a joystick.
- Protective Shield: Activation of a shield when the hand approaches the ultrasonic sensor.
- Projectile Shooting: Ability to shoot projectiles by pressing the joystick button.
- Active Enemies: An enemy that chases the player and must be avoided or eliminated.
- Item Collection: Items that appear on the screen and can be collected to increase the score.
- Scoring System: The score increases by collecting items and hitting the enemy.
- Game Over Screen: Display of a "Game Over" screen with the option to restart.

HARDWARE REQUIREMENTS

- Arduino Uno (or compatible)
- Analog Joystick (with X and Y axes and a button)
- HC-SR04 Ultrasonic Sensor
- Connecting Wires
- Computer with USB Port

SOFTWARE REQUIREMENTS

- Python 3.x
- Pygame Library: Installable with pip install pygame
- PySerial Library: Installable with pip install pyserial
- Arduino IDE: To upload the code to the Arduino

HARDWARE CONNECTION DIAGRAM

- Joystick
VRx → A0 (Arduino)
VRy → A1 (Arduino)
SW → D2 (Arduino)
VCC → 5V (Arduino)
GND → GND (Arduino)

- HC-SR04 Ultrasonic Sensor
Trig → D9 (Arduino)
Echo → D10 (Arduino)
VCC → 5V (Arduino)
GND → GND (Arduino)

INSTALLAZIONE

- Clone the Repository
git clone https://github.com/your-username/your-project.git

- Install Python Dependencies
pip install pygame pyserial

- Upload the Code to Arduino

- Open the file arduino_code.ino in the Arduino IDE.
Select the correct port and board type.
Upload the code to the Arduino.

USAGE
- Connect Arduino to the Computer
Ensure the Arduino is connected via USB.

- Run the Python Script
python main.py

GAME CONTROLS
- Movement: Use the joystick to move the character.
- Shooting: Press the joystick button to shoot projectiles.
- Shield: Bring your hand close to the ultrasonic sensor to activate the shield.
- Restart: After a "Game Over," push the joystick upward to restart.

CODE STRUCTURE
- main.py: Main script that runs the game.
- arduino_code.ino: Arduino code to read the joystick, ultrasonic sensor, and send data to the computer.

FUNCTIONALITY EXPLANATION
- Communication Between Arduino and Python
The Arduino reads values from the joystick, button, and ultrasonic sensor, sending data to the computer via the serial port. The Python script receives this data and uses it to control the game in real-time.

GAME MECHANICS
- Character Movement: Based on the joystick's X and Y values.
- Shield Activation: When the distance detected by the sensor is less than 10 cm, the shield activates for a duration of 2 seconds.
- Projectile Shooting: The joystick button allows the player to shoot projectiles that can eliminate the enemy.
- Enemy: A red square that chases the player; if it touches the player without the shield, the game ends.

CONTRIBUTING
If you'd like to contribute to the project:
1. Fork the Repository
2. Create a New Branch
git checkout -b feature/feature-name
3. Make Your Changes
4. Commit Your Changes
git commit -m "Added a new feature"
5. Push the Branch
git push origin feature/feature-name
6. Open a Pull Request

ACKNOWLEDGEMENTS
- Pygame Library: For providing excellent tools for game development in Python.
- Arduino Community: For the support and available resources.



