# Goal Tracker

## About
A goal tracker that uses objectives, key results, and tasks to keep you accountable. Tasks are numeric or boolean. Tasks can be configured at different recurrences; daily, weekly, one-time, etc.

[*More information about objective and key result (OKR)*](https://en.wikipedia.org/wiki/OKR)

## Definitions

- *Objective*
    - A clearly defined goal
- *Key Result*
    - A measurable success criteria used to track attainment of an objective. There can be many key results associated with one objective.
- *Task*
    - A concrete activity that needs to be accomplished to track attainment of a key result. There can be many tasks associated with one key result.

## Demo Instructions

### One-time Set-Up
1. [Clone the Github repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) to your local environemnt.
1. `cd` to the repository in your local environment.
1. Create a Python virtual environment. In the examples below, we set up a virtual environment called `.venv`

        python3 -m venv .venv

1. Activate the Python virtual environment.

        source .venv/bin/activate

1. Use `pip` to install the dependencies.

        pip install -r requirements.txt
1. Set up the SQLite database.
    1. Open a new terminal in the same directory and run `python3`.
    1. In the python3 terminal, run

        ```
        from app import app
        from app import db
        with app.app_context():
            db.create_all()
        ```

    *TIP: Use [DB Browser for SQLite](https://sqlitebrowser.org/) for a SQLite GUI interface.*

### Running the Flask web app locally
1. `cd` to the repository in your local environment.
1. Activate the Python virtual environment.

        source .venv/bin/activate
1. Run

        flask --app app.py --debug run

1. In the command's output, you'll see a line such as `Running on http://127.0.0.1:5000`. Navigate to the site listed to access the web app on your browser.