import module_google_proj as mgp

def main():

    '''
    events = get_values_calendar()
    pprint(events)
    #for event in events:
    #    start = event['start'].get('dateTime', event['start'].get('date'))
    #    print(start, event['summary'])
    '''
    sheetval = mgp.get_sheet_values('test')
    print(sheetval)

if __name__ == __main__:
    main()