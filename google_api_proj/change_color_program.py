import module_google_proj as mgp
from pprint import pprint 
import time

def main():
   
    print("Bitte nur Zahlen eingeben!")
    executed = False
    
    while executed == False:
        try:
            count = int(input("Wie viele Events sollen gecheckt werden?"))
            print(
            '''    1 Lavender \n
            2 Sage \n
            3 Grape	 \n
            4 Flamingo \n	
            5 Banana \n
            6 Tangerine	\n
            7 Peacock \n
            8 Graphite \n
            9 Blueberry \n
            10 Basil \n
            11 Tomato \n''')
            color_code = int(input("Color Code eingeben:"))
            executed = mgp.change_colour_events(count, color_code)
        
        except ValueError:
            print("Das war keine Zahl! Bitte nur Zahlen eingeben!")
        except TypeError: 
            print("Das war keine Zahl! Bitte nur Zahlen eingeben!")
        except Exception as e:
            print(e)
        
    print('Done!')
    time.sleep(2)

if __name__ == "__main__":
    main()