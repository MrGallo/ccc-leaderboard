# ccc-leaderboard

## Requirements
As outlined in the `pyproject.toml`:
- Pygame
- Requests

## Instructions

1. Create a `.credentials` file with the teacher login and pass on separate lines.
2. Edit the `JR_NUMBER` and `SR_NUMBER` (in `leaderboard.py`) to the current contest's id. These ids are found in the link to view the CCC leaderboard chart in the cccgrader teacher section.
3. Run `leaderboard.py`
4. Press `f` to toggle full screen mode.
5. You may have to adjust the `WIDTH` and `HEIGHT` of the window in `leaderboard.py`, 
according to the display you are using.

The junior chart is on the left, the senior on the right.

Only students with points will show up. 

The tables are updated every 20 seconds.

You can set `DEV_MODE = True` and it will load a previous year's tables (to ensure it actually works).

## Opting-out Students
If students wish not to have their names displayed, create a `.opt-out` file and populate it with all the CCC grader usernames that you wish to be anonymized. One username per line.

Note: the usernames are **not** the email addresses. They are a short string in the format "first letter of the first name + some last name + a number (possibly)". For example `dgallo1`.

