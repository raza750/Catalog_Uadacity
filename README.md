<h3>Item-Catalog</h3>
<p>Create a movie database app where users can add, edit, and delete movies.</p>

<h5>Setup and run the project</h5>
Prerequisites</br>
Python</br>
Vagrant</br>
VirtualBox</br>
<h5>How to Run</h5>
Install VirtualBox and Vagrant</br>
Clone this repo(https://github.com/raza750/Catalog_Uadacity)</br>
Unzip and place the Item Catalog folder in your Vagrant directory</br>
<h5>Launch Vagrant</h5>
$ Vagrant up 
Login to Vagrant
$ Vagrant ssh
Change directory to /vagrant
$ Cd /vagrant
<p>Initialize the database</p>
$ Python database.py
<p>Populate the database with some initial data</p>
$ Python dummyData.py
<p>Launch application</p>
$ Python appone.py
Open the browser and go to http://localhost:5000
<h5>JSON endpoints</h5>
<p>Returns JSON of all Genre</p>
/genre/JSON
<p>Returns JSON of Movies based on Genre</p>
/genre/<int:genre_id>/movie/JSON
