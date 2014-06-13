from sqlalchemy import (Column, Integer, String, ForeignKey, UniqueConstraint,
                        Boolean, Float, DateTime, Table, create_engine, and_, event)
#from sqlalchemy.orm import (relationship, backref, sessionmaker, scoped_session,
#                            mapper)
from flask.ext.sqlalchemy import SQLAlchemy                            

from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_ECHO'] = False
app.debug = True
app.secret_key = 'Todo'
                            
db = SQLAlchemy(app)

    
class Group(db.Model):
    id =  Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    def __repr__(self): return self.name
    

class Team(db.Model):
    id =  Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    
    group_id = Column(Integer, ForeignKey(Group.id), nullable=False)
    group = db.relationship(Group, backref=db.backref('teams'))
    
    def __repr__(self): return '[Gruppe %s] %s' % (self.group.name, self.name)
    
    
class GameType(db.Model):
    id =  Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    def __repr__(self): return self.name
    
    
class Game(db.Model):
    id =  Column(Integer, primary_key=True)
    
    game_type_id = Column(Integer, ForeignKey(GameType.id), nullable=False)
    game_type = db.relationship(GameType, backref=db.backref('games'))
    
    team_a_id = Column(Integer, ForeignKey(Team.id), nullable=False)
    team_a = db.relationship(Team, foreign_keys=team_a_id)
    team_a_score = Column(Integer)
    
    team_b_id = Column(Integer, ForeignKey(Team.id), nullable=False)
    team_b = db.relationship(Team, foreign_keys=team_b_id)
    team_b_score = Column(Integer)
    
    date = Column(DateTime, nullable=False)
    
    def __repr__(self): return '%s - %s' % (self.team_a.name, self.team_b.name)
    
    
class Tipper(db.Model):
    id =  Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    def __repr__(self): return self.name
    
    
class Tipp(db.Model):
    id =  Column(Integer, primary_key=True)
    
    tipper_id = Column(Integer, ForeignKey(Tipper.id), nullable=False)
    tipper = db.relationship(Tipper, backref='tipps')
    
    game_id = Column(Integer, ForeignKey(Game.id), nullable=False)
    game = db.relationship(Game, backref='games')
    
    team_a_tipp = Column(Integer, nullable=False)
    team_b_tipp = Column(Integer, nullable=False)
    
    def __repr__(self): return '%s: %s - %s' % (game.__unicode__(), team_a_tipp, team_b_tipp)



if __name__ == '__main__':
    from flask.ext.admin import Admin
    from flask.ext.admin.contrib.sqla import ModelView
    

    db.create_all()
    
    group_a = Group(name='A')
    halbfinale = GameType(name='Halbfinale')
    deutschland = Team(name='Deutschland', group=group_a)
    england = Team(name='England', group=group_a)
    ben = Tipper(name='Ben')
    sarina = Tipper(name='Sarina')
    
    #db.session.add_all([group_a, halbfinale, deutschland, england, ben, sarina])
    db.session.commit()
    
    session = db.session
    
    admin = Admin(app)
    admin.add_view(ModelView(Group, session))
    admin.add_view(ModelView(Team, session))
    admin.add_view(ModelView(GameType, session))
    admin.add_view(ModelView(Game, session))
    admin.add_view(ModelView(Tipper, session))
    admin.add_view(ModelView(Tipp, session))
    
    app.run(port=5555)
    
    
    
