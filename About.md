**About**

The system was designed on request for a care home in Hove (near Brighton) to track staff members' shifts with an accessible, intuitive summary available to the care home director. After researching multiple options, the solution I decided would be most appropriate is a keycard check-in-check-out. 
From the perspective of a staff member, whenever they start or end their shift, they should take their named keycard from the rack (next to the scanner) and tap it on the RFID pad until they hear a tone. This tone sounds when the keycard has been scanned and it should be followed by a notification on a screen next to the RFID pad which should state the action that is being completed (check in or out). The screen also shows the date, time, and a list of currently checked-in people.
From the perspective of the director, the system is connected to a Google Sheet using the Google Sheets API. This Google Sheet includes info on who is checked in, a log of people checking in/out, past shifts + shift lengths, and names of people registered on the system with a keycard. The director can manage who is checked in by simply removing/adding a record of their name under the checked-in section.
The workings of the system are all programmed in Python (aside from the off JSON file). The code is split into two sections: The frontend (GUI) and the backend (main program). The backend carries out all the processing and data storage while the front end is simply updated using a function call to display the relevant information on the GUI. Both the frontend and the backend run asynchronously to each other.
The location for the data storage is on the Google Sheet (so as to provide maximum control for the care home director) and the Raspberry Pi works by backlogging actions that require a change in the stored data until they have been completed by amending the Google Sheet. This means actual data for who is checked in is copied from the sheet to the local file at regular intervals (and never the other way round).
The system is designed to be fully robust (you can't break it!).  In the event of a power cut (even right after a keycard scan), the system would already have status and incomplete actions saved to the backlog files which would be loaded back into the program when it automatically starts up when power returns (this was done using a Raspberry Pi SystemD service). Should the internet cut out or connection fail to the Google Sheet, all actions will be added to a backlog and be applied as soon as connection is established. The system can also cope easily with a stress test on the keycard scanning as actions are simply added to a backlog file and dealt with as soon as there is time to process them.
The system is designed to allow for new staff members to be added or old ones to be removed easily. Members can be removed (or swapped out) by simply renaming the record of the staff member on the google sheet. A new staff member can be added by scanning a totally new RFID card on the machine. This will not check anyone in and will instead add a new record to the registered staff members section of the sheet ready for you to add a name. It's as simple as that.
The hardware components consist of a Raspberry Pi 4B, RFID scanner and a buzzer which are connected using GPIO pins to the Raspberry Pi and the Official Raspberry Pi 7" Touchscreen which is connected to the Raspberry Pi using the DSI port. Additional components to the system include the RFID cards and a rack to store the cards.