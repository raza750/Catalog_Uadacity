Item-Catalog
Create a movie database app where users can add, edit, and delete movies.

Setup and run the project
Prerequisites
Python 
Vagrant
VirtualBox
How to Run
Install VirtualBox and Vagrant
Clone this repo(https://github.com/raza750/Catalog_Uadacity)
Unzip and place the Item Catalog folder in your Vagrant directory
Launch Vagrant
$ Vagrant up 
Login to Vagrant
$ Vagrant ssh
Change directory to /vagrant
$ Cd /vagrant
Initialize the database
$ Python database.py
Populate the database with some initial data
$ Python dummyData.py
Launch application
$ Python appone.py
Open the browser and go to http://localhost:5000
JSON endpoints
Returns JSON of all Genre
/genre/JSON
Returns JSON of Movies based on Genre
/genre/<int:genre_id>/movie/JSON
