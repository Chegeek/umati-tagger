umati-tagger
============

About
A web platform that will be can be used to tag textual or conversational data collected and stored in a database. Borne out of the need to request collaborators to a tagging session without having to send the data to them and well as request the users to resend the data back. 

### Installation Pre-requisites

1. python 2.7 or up
2. python Flask library with Flask-mail-ext
3. psycopg2 library or any other library to your database
4. redis database
5. python redis library
6. 

### Steps to run the tagger on your machine

1. Download the zip folder of the master branch
2. Unzip the zip folder
3. In your command line, go to umati-tagger folder
4. Open the settings.py and change the app configuration, mail server and database it will connect to
5. Run app.py and open the localhost address which it will broradcast to
6. 

### Using the app 
#### Creating Sessions
To tag data an app administrator will have created a tag session for the user. This menu option is found on the home page of the app. The app will request the administrator's password and redirect to the page to create tagging sessions. Creating tagging sessions involves first creating a question or prompt that will be answered by the tags. The second step involves specifying the user who will be requested to tag. The details include their name, email address (which will be used to send a link with the tagging session) and the number of records. On completion the app will send emails to the specified users inviting them to tag the data.

#### Tagging
Follow the link sent to users email address. Tag the data by pressing the keys specified on the form, e.g. pressing 'Y' or 'N' to respond to the prompt specified. If a mistake was made a user can click the record in the table and it will be placed back in the tagging label section, and the user can correct the entry.
