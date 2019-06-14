#!/usr/bin/env python3f
rom sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Genre, Base, Movie, User

engine = create_engine('sqlite:///movies.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

User1 = User(name="admin", email="admin1@gmail.com")
session.add(User1)
session.commit()
read = session.query(User).all()
for r in read:
	print(r.name + " " +str(r.id) + " " + r.email)
	
horror = Genre(name="Horror")
session.add(horror)
session.commit()

action = Genre(name="Action")
session.add(action)
session.commit()

comedy = Genre(name="Comedy")
session.add(comedy)
session.commit()

drama = Genre(name="Drama")
session.add(drama)
session.commit()

read = session.query(Genre).all()
for r in read:
	print(r.name + " " +str(r.id))

conjuring = Movie(name="Conjuring", description="this is a horror movie",
                     rating=4, genre=horror, user=User1)

session.add(conjuring)
session.commit()	

ironman = Movie(name="Iron Man",description="this is an action movie",
                     rating=2, genre=action, user=User1)

session.add(ironman)
session.commit()

golmaal = Movie(name="Golmaal",description="this is a comedy movie",
                     rating=3, genre=comedy, user=User1)

session.add(golmaal)
session.commit()

titanic = Movie(name="Titanic",description="this is a drama movie",
                     rating=5, genre=drama, user=User1)

session.add(titanic)
session.commit()

read = session.query(Movie).all()
for r in read:
	print(r.name + " " +str(r.id) + " " + r.description+ " " +str(r.rating) + " " + str(r.genre_id) + " " + str(r.user_id))
	
print "Added movies!"