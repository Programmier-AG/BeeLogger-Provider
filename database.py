import flask_sqlalchemy


client = flask_sqlalchemy.SQLAlchemy()

class Config(client.Model):
    __tablename__ = "config"
    key = client.Column(client.String(255), primary_key=True)
    value = client.Column(client.String(255))

class DataBackup(client.Model):
    __tablename__ = "data_backup"
    number = client.Column(client.Integer, primary_key=True, autoincrement=True)
    temperature = client.Column(client.FLOAT, default=None)
    weight = client.Column(client.FLOAT, default=None)
    humidity = client.Column(client.FLOAT, default=None)
    measured = client.Column(client.DateTime, default=None)

class Logs(client.Model):
    id = client.Column(client.Integer, nullable=False, primary_key=True, autoincrement=True)
    time = client.Column(client.DateTime)
    source = client.Column(client.String(255))
    message = client.Column(client.TEXT)
    code = client.Column(client.Integer)
