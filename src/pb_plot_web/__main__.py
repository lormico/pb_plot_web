from flask import Flask, render_template
from pb_analyzer.configuration import load_config
from pb_analyzer.persistence import get_db_session
from pb_analyzer.persistence.models import Station, Price, Metadata

app = Flask(__name__)
config = load_config()


def main():
    app.run(host='0.0.0.0')


@app.route('/')
def home():
    return render_template('plotly_index.html', graphData=load_plots(), lastUpdate=get_last_updated())


def load_plots():
    with get_db_session(config["PERSISTENCE"]["db_file"]) as db_session:
        plots = list()
        for station in db_session.query(Station):
            prices = db_session.query(Price.date, Price.price).filter(Price.fuel == "benzina",
                                                                      Price.station == station.id,
                                                                      Price.service != "CS").all()
            plots.append(
                dict(
                    x=[price[0].strftime("%Y-%m-%d %H:%M:%S") for price in prices],
                    y=[float(price[1]) for price in prices],
                    type="scatter",
                    name=station.name
                )
            )

    return plots


def get_last_updated():
    with get_db_session(config["PERSISTENCE"]["db_file"]) as db_session:
        last_updated, = db_session.query(Metadata.value).filter(Metadata.key == "last_updated").one()
    return last_updated


if __name__ == '__main__':
    main()
