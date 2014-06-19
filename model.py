from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Group(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def __repr__(self): return self.name


class Team(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    group_id = db.Column(db.Integer, db.ForeignKey(Group.id), nullable=False)
    group = db.relationship(Group, backref=db.backref('teams'))

    def __repr__(self): return self.name


class GameType(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def __repr__(self): return self.name


class Game(db.Model):
    id =  db.Column(db.Integer, primary_key=True)

    game_type_id = db.Column(db.Integer, db.ForeignKey(GameType.id), nullable=False)
    game_type = db.relationship(GameType, backref=db.backref('games'))

    team_a_id = db.Column(db.Integer, db.ForeignKey(Team.id), nullable=False)
    team_a = db.relationship(Team, backref=db.backref('games_as_team_a'), foreign_keys=team_a_id)
    team_a_score = db.Column(db.Integer)

    team_b_id = db.Column(db.Integer, db.ForeignKey(Team.id), nullable=False)
    team_b = db.relationship(Team, backref=db.backref('games_as_team_b'), foreign_keys=team_b_id)
    team_b_score = db.Column(db.Integer)

    date = db.Column(db.DateTime, nullable=False)

    def __repr__(self): return '%s - %s' % (self.team_a.name, self.team_b.name)


    def repr_score(self):
        if self.team_a_score is not None:
            return '{0.team_a_score} : {0.team_b_score}'.format(self)
        else:
            return ''




class Tipper(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def __repr__(self): return self.name


class Tipp(db.Model):
    id =  db.Column(db.Integer, primary_key=True)

    tipper_id = db.Column(db.Integer, db.ForeignKey(Tipper.id), nullable=False)
    tipper = db.relationship(Tipper, backref='tipps')

    game_id = db.Column(db.Integer, db.ForeignKey(Game.id), nullable=False)
    game = db.relationship(Game, backref='tipps')

    team_a_tipp = db.Column(db.Integer, nullable=False)
    team_b_tipp = db.Column(db.Integer, nullable=False)

    def __repr__(self): return '%s: %s - %s' % (self.game.__repr__(), self.team_a_tipp, self.team_b_tipp)

    def get_score(self):
        if self.game.team_a_score is None:
            return None

        elif self.game.team_a_score == self.team_a_tipp and \
             self.game.team_b_score == self.team_b_tipp:
            return 3

        elif (self.game.team_a_score > self.game.team_b_score and self.team_a_tipp > self.team_b_tipp) or \
             (self.game.team_a_score < self.game.team_b_score and self.team_a_tipp < self.team_b_tipp):
            return 1

        else:
            return 0



from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView


from flask import Flask, render_template

app = Flask(__name__)
app.config['SQLALCHEMY_ECHO'] = False
app.secret_key = 'Todo'

db.init_app(app)
with app.test_request_context():
    db.create_all(app=app)

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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def teams():
    return render_template('teams.html', groups=Group.query.all())

@app.route('/games')
def games():
    return render_template('games.html', games=Game.query.all())

@app.route('/tippers')
def tippers():
    res = db.engine.execute('''
        select
            t.id,
            t.name,
            sum(
                case
                    when ti.team_a_tipp = g.team_a_score and ti.team_b_tipp = g.team_b_score then 3
                    when
                        (g.team_a_score > g.team_b_score and ti.team_a_tipp > ti.team_b_tipp) or
                        (g.team_a_score < g.team_b_score and ti.team_a_tipp < ti.team_b_tipp)
                    then 1
                    else 0 end
            )as score
        from tipper t
        join tipp ti on t.id = ti.tipper_id
        join game g on ti.game_id = g.id
        where g.team_a_score is not null
        group by t.id
    ''')
    return render_template('tippers.html', tippers=res)

@app.route('/team/view/<int:team_id>')
def team(team_id):
    return render_template('team.html', team=Team.query.get(team_id))

@app.route('/game/view/<int:game_id>')
def game(game_id):
    return render_template('game.html', game=Game.query.get(game_id))

@app.route('/tipper/view/<int:tipper_id>')
def tipper(tipper_id):
    ((total_score, ), ) = db.engine.execute('''select
            sum(
                case
                    when ti.team_a_tipp = g.team_a_score and ti.team_b_tipp = g.team_b_score then 3
                    when
                        (g.team_a_score > g.team_b_score and ti.team_a_tipp > ti.team_b_tipp) or
                        (g.team_a_score < g.team_b_score and ti.team_a_tipp < ti.team_b_tipp)
                    then 1
                    else 0 end
            )as score
        from tipper t
        join tipp ti on t.id = ti.tipper_id
        join game g on ti.game_id = g.id
        where
            g.team_a_score is not null and
            t.id = :tipper_id
        group by t.id
    ''', tipper_id=tipper_id)

    return render_template('tipper.html', tipper=Tipper.query.get(tipper_id), total_score=total_score)


if __name__ == '__main__':
    app.debug = True
    app.run(port=5555)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
else:
    import os
    import logging

    file_handler = logging.FileHandler('/home/www/whowillwin/whowillwin.log')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))

    app.logger.addHandler(file_handler)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/www-data/whowillwin/db.sqlite'
