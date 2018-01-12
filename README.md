Movie Catalog
 Project Overview
 
 This project is CRUD application, users can login with oauth Google. 

  1. Install Vagrant and VirtualBox
  2. Download or Clone (https://github.com/udacity/fullstack-nanodegree-vm) repository. 
  3. Unzip the project folder inn catalog folder. 
 
  
Launching the Virtual Machine:
  1. Launch the Vagrant VM inside Vagrant sub-directory in the downloaded fullstack-nanodegree-vm repository in your shell using command:
   vagrant up
 
  2. Then Log into this using command:
   vagrant ssh

  3. Change directory to /vagrant /catalog
  
 Launching the application:
   From the vagrant directory inside the virtual machine

  1. Setup the database.
  
  
     python database_setup.py
  
  2. To insert default movie data 
  
    python movies.py

  3.To start the web browser:
  
   python application.py
   
  4. open browser to view the web application
   http://localhost:8000/genre

  
	
	
Features:

1.Can access JSON data at the following pages:
  -> All Genres: [http://localhost:8000/genre/JSON
  -> Movies in specific genre: [http://localhost:8000/genre/\<genre_id\>/JSON
  -> Specific movie : [http://localhost:8000/genre/\<genre_id\>/\<movie_id\>/JSON
2.Users can login / logout with Google Plus sign in.
3. Users cannot Get or Post New, Edit, or Delete movies without sign in into the account.
4. Users cannot Get or Post Edit or Delete movies without being the original creators of the movie.
4. Logged in users can create new movie.

  
  