from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class 控制設備(Action):

    def name(self) -> Text:
        return "控制設備"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        import RPi.GPIO as GPIO
        from RPLCD.i2c import CharLCD

        lcd = None

        GPIO.setwarnings(False)

        # RPi pin mode = BOARD

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(11, GPIO.OUT)


        try:
            GPIO.output(11, GPIO.HIGH)
            lcd = CharLCD(i2c_expander='PCF8574', address=0x27, backlight_enabled=True, auto_linebreaks=True)
            lcd.write_string('Hello World !')
        except Exception as e:
            print(e)

