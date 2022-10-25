import module_google_proj as mgp
from pprint import pprint
import time


def main():

    executed = False
    main_key = "Schulung Burgenland"
    alternative_key = "Kurs!"
    while executed == False:
        try:
            choose_funct = int(
                input(
                    "Welche Funktion willst du ausführen? Color Change(1) oder Add driving time(2), bitte gib die Zahl ein."
                )
            )

            if choose_funct == 1:  # change color function was chosen

                count = int(
                    input("Wie viele Events sollen gecheckt werden?(Nur Zahl eingeben)")
                )
                key_change = input(
                    'Willst du den Key ändern? Derzeit ist der Organizer Key: "Schulung Burgenland" und der Event Name Key: "Kurs!" Schriebe [J] für Ja oder [N] für Nein:'
                )

                if key_change == "J":

                    main_key = input(
                        'Gib deinen neuen Organizer Key ein, wenn du den Organizer nicht checken willst gib "Ignorieren" ein:'
                    )
                    alternative_key = input(
                        "Gib deinen neuen Event Name Key [Name Event, oder Teil vom Namen] ein:"
                    )

                print(
                    """    1 Lavender (KTM)\n
                2 Sage \n
                3 Grape	(Helene) \n
                4 Flamingo \n	
                5 Banana \n
                6 Tangerine	\n
                7 Peacock \n
                8 Graphite (Fahrzeit)\n
                9 Blueberry \n
                10 Basil (Kurse)\n
                11 Tomato (WU) \n"""
                )
                color_code = int(input("Color Code eingeben:"))

                executed = mgp.change_colour_events(
                    count, color_code, main_key, alternative_key
                )

            if choose_funct == 2:

                event_count = int(input("Wie viele Events willst du checken?"))
                executed = mgp.add_driving_time(event_count)

            else:
                print("Bitte eine der möglichen Zahlen für die Funktionen eingeben.")

        except ValueError:
            print("Das war keine Zahl! Bitte nur Zahlen eingeben!")
        except TypeError:
            print("Das war keine Zahl! Bitte nur Zahlen eingeben!")
        except Exception as e:
            print(e)

    print("Done!")
    time.sleep(2)


if __name__ == "__main__":
    main()
