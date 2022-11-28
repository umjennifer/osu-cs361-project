# Goal Tracker

A goal tracker that uses objectives, key results, and tasks to keep you accountable. A goal == an objective.

Each objective has associated key result(s). Each key result has associated task(s). Tasks can be configured at different recurrences: one-time, daily, weekly, yearly.

Users can review and check off their tasks for each day. By doing this, the user will have a daily reminder of what they're working towards.

[*More information about objective and key result (OKR)*](https://en.wikipedia.org/wiki/OKR)

## About
I used to set goals for myself at the start of the year (ex: *create a personal software project, watch all 1000+ episodes of the One Piece anime, etc.*) but by the time June would come around, I'd look at my list of goals and realize I had forgotten about them completely. 

This tracker solves that issue by breaking down each goal (referred to as an *objective*) into measurable, success criteria(s) (referred to as *key result(s)`*), then breaking down each key result(s) into various task(s) (recurring, or one-time only) that are reviewed daily.

## Definitions

- *Objective*
    - A clearly defined goal
- *Key Result*
    - A measurable success criteria used to track attainment of an objective. There can be many key results associated with one objective.
- *Task*
    - A concrete activity that needs to be accomplished to track attainment of a key result. There can be many tasks associated with one key result.

## Example of an OKR with Tasks

### Example

- **Objective**: Post more vlogs on YouTube
    - **Key Result**: Post one video per week between October 1, 2022 and November 31, 2022
        - **Task**: Brainstorm ideas once a month between October 1, 2022 and November 31, 2022
        - **Task**: Finalize ideas
        - **Task**: Schedule time for recording
        - **Task**: Schedule time for editing
        - **Task**: Create publishing schedule
        - **Task**: Edit video 1x/week
        - **Task**: Publish video 1x/week 
    - **Key Result**: Create a YouTube profile pic
        - **Task**: Spike Test Canva
        - **Task**: Spike Test Procreate
        - **Task**: Research popular profile pics
        - **Task**: Create and publish profile pic
   - **Key Result**: Research and document trends
        - **Task**: Look up viral videos 1x/week

### UI Example
Screenshots from v1.0. Note that an objective is listed in an accordian, which contains accordians for each associated key result. Each associated key result contains accordians for each associated task.
![Objective Example](/README-images/objective.png)
![Key Results Example](/README-images/key-result.png)
![Tasks Example](/README-images/tasks.png)

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
