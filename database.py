import flask_sqlalchemy


client = flask_sqlalchemy.SQLAlchemy()

class Config(client.Model):
    __tablename__ = "config"
    key = client.Column(client.String(255), primary_key=True)
    value = client.Column(client.String(255))

class DataBackup(client.Model):
    __tablename__ = "data_backup"
    number = client.Column(client.BIGINT, nullable=False, primary_key=True, autoincrement=True)
    temperature = client.Column(client.FLOAT, default=None)
    weight = client.Column(client.FLOAT, default=None)
    humidity = client.Column(client.FLOAT, default=None)
    measured = client.Column(client.DateTime, default=None)
