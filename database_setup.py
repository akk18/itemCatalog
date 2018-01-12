from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import asc, desc


Base = declarative_base()

engine = create_engine('sqlite:///movies.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# User functions
def create_user(login_session):
    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
        )

    session.add(new_user)
    session.commit()
    return new_user.id


def get_user(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(250))
    picture = Column(String)


# Genre functions
def create_genre(name):
    new_genre = Genre(name=name)
    session.add(new_genre)
    session.commit()
    return new_genre.id


def get_genre(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    return genre


def get_genre_id(name):
    genre = session.query(Genre).filter_by(name=name).one()
    return genre.id


def get_movies(genre_id):
    movies_list = session.query(Movie).join(Movie.genre).filter_by(id=genre_id)
    return movies_list


def get_all_genre():
    genres = session.query(Genre).order_by(asc(Genre.name))
    return genres


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


# Movie functions
def create_movies(name, description, genre_id, user_id):
    new_movie = Movie(
        name=name,
        description=description,
        genre_id=genre_id,
        user_id=user_id
        )
    session.add(new_movie)
    session.commit()
    return new_movie


def get_movie(movie_id):
    movie = session.query(Movie).filter_by(id=movie_id).one()
    return movie


def delete_movie(movie):
    session.delete(movie)
    session.commit()


def edit_movie(movie, name, description, genre_id):
    movie.name = name
    movie.description = description
    movie.genre_id = genre_id
    session.add(movie)
    session.commit()
    return movie


class Movie(Base):
    __tablename__ = 'movie'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(Text)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'genre': self.genre.name
        }

if __name__ == '__main__':
    Base.metadata.create_all(engine)
