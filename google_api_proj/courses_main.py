import module_google_proj as mgp
from pprint import pprint 

def main():

    #free_courses, my_courses = mgp.get_sheet_values('test')
    #cleaned_free_courses = mgp.clean_sheet_values(free_courses)
    #print(cleaned_free_courses)
    #events_calendar = mgp.get_values_calendar(10)
    #for event in events_calendar: 
    #    pprint(event)
    #events_final = mgp.compare_calendar_sheets(cleaned_free_courses, events_calendar)
    #print(events_final)
    mgp.change_colour_events(10, 10)
        
            

if __name__ == "__main__":
    main()