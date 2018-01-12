from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Genre, Movie, engine


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# User functions
def create_user(name, email, picture):
    new_user = User(
        name=name,
        email=email,
        picture=picture
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





# Genre functions
def create_genre(name):
    new_genre = Genre(name=name)
    session.add(new_genre)
    session.commit()
    return new_genre.id


def get_genre_id(name):
    genre = session.query(Genre).filter_by(name=name).first()
    return genre.id


def get_movies(genre_name):
    movies_list = session.query(Movie).join(Movie.genre).filter_by(name=genre_name)
    return movies_list


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
    return new_movie.id


# set up functions:

def add_users():
    user_list = [
        ['Anil Kodali', 'anil.kodali@gmail.com', 'http://picture_url.com']
    ]

    for user in user_list:
        create_user(user[0], user[1], user[2])

# Default genres
def fill_genre():
    genre_list = [
        'Action',
        'Comedy',
        'Education',
        'Fiction',
		'Horror',
        'Kids',
        'Science'
    ]

    for genre in genre_list:
        create_genre(genre)

# Inserting default movies into the database
def fill_movies():

    movies = [
        (
            'Logan',
            'In the near future, a weary Logan cares for an ailing Professor X, somewhere on the Mexican border. However, Logan\'s attempts to hide  his legacy, are upended when a young mutant arrives, pursued by dark force',
            'Action'
            ),
        (
            'John Wick',
            'After returning to the criminal underworld to repay a debt, John Wick discovers that a large bounty has been put on his life.',
            'Action'
            ),
        (
            'Cult of Chucky',
            'hucky returns to terrorize his human victim, Nica. Meanwhile, the killer doll has some scores to settle with his old enemies, with the help of his former wife',
            'Horror'
            ),
        (
            'Annable:Creation',
            '12 years after the tragic death of their little girl, a dollmaker and his wife welcome a nun and several girls from a shuttered orphanage into their home, where they soon become the target of the dollmaker\'s possessed creation, Annabelle',
            'Horror'
            ),
        (
            'Bay Watch',
            'Devoted lifeguard Mitch Buchannon butts heads with a brash new recruit, as they uncover a criminal plot that threatens the future of the bay.',
            'Comedy'
            ),
        (
            'The Big Sick',
            'Pakistan-born comedian Kumail Nanjiani and grad student Emily Gardner fall in love but struggle as their cultures clash. When Emily contracts a mysterious illness, Kumail finds himself forced to face her feisty parents, his family\'s expectations, \and his true feelings.',
            'Comedy'
            ),
        (
            'Jumanji',
            'Four teenagers are sucked into a magical video game, and the only way they can escape is to work together to finish the game.',
            'Fiction'
            ),
        (
            'Beauty and the Beast',
            'An adaptation of the fairy tale about a monstrous-looking prince and a young woman who fall in love.',
            'Fiction'
            ),
        (
            'Justice League',
            'Fueled by his restored faith in humanity and inspired by Superman\'s selfless act, Bruce Wayne enlists the help of his newfound ally, Diana Prince, to face an even greater enemy.',
            'Action'
            ),
        (
            'Wonder Woman',
            'When a pilot crashes and tells of conflict in the outside world, Diana, an Amazonian warrior in training, leaves home to fight a war, discovering her full powers and true destiny.',
            'Action'
            ),
        (
            'Transformers: The Last Knight',
            'a Spielberg-inspired, boy-and-his-car adventure starring Shia LaBeouf and 8 bazillion CG pixels, the robotic franchise has devolved into a monotone string of horn-blaring, metal-ripping, problematic pieces of blockbuster blah',
            'Science'
            ),
        (
            'Guardians of the Galaxy, Vol. 2',
            'tar-Lord, Gamora, Drax, Rocket Raccoon, and Baby Groot needed to come to life and become more than pawns in a game of Infinity Stone chess. In Vol. 2, Gunn splits up the gang and drops them in increasingly manic situations, like an intergalactic version of a \'70s-era Looney Tunes compilations',
            'Science'
            ),
        (
            'Dead Poets Society',
            'A teacher who inspires his students to challenge the norm through his teaching of poetry.',
            'Education'
            ),
        (
            'School Ties',
            'A movie set in the 1950 that deals with anti-Semitism and can easily be applied to discrimination of all types.',
            'Education'
            ),
        (
            'Boss Baby',
            'A suit-wearing, briefcase-carrying baby pairs up with his 7-year old brother to stop the dastardly plot of the CEO of Puppy Co.',
            'Kids'
            ),
        (
            'Coco',
            'Aspiring musician Miguel, confronted with his family\'s ancestral ban on music, enters the Land of the Dead to find his great-great-grandfather, a legendary singer.',
            'Kids'
            )
    ]

    for m in movies:
        create_movies(
            m[0],
            m[1],
            get_genre_id(m[2]), 
			1
            
            )


if __name__ == '__main__':
    add_users()
    fill_genre()
    fill_movies()
