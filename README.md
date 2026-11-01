# J! Archive Game

A pass-the-iPad trivia game using real *Jeopardy!* clues, with each clue's original air date.

The game is a single web page (`index.html`). **It contains no clues.** Each device loads a
private clue file once, and the game keeps it in the browser's storage. That way the website
can be public while the copyrighted clue data stays private.

## Playing

1. Open the game's web address in Safari or Chrome.
2. Tap **Load clue file…** and choose `jeopardy-clues.json.gz`. You only do this once per device.
3. Add players, pick a year range and show types, and tap **Start new match**.
4. On each turn the player sees the category, value and air date, then taps **Show clue**,
   answers out loud, taps **Reveal response**, and the group judges it **Correct** or **Incorrect**.
5. If the player doesn't know, anyone else can **Steal** after the clue is shown: tap their name
   before revealing the response. The player who didn't know loses the clue's value, and
   the stealer wins or loses it depending on their answer. Turns keep rotating as usual. Daily Doubles can't be stolen.
6. Like a category? Tap **Run this category** to play the rest of that category's clues (from
   the same game and round, lowest value first) before going back to random clues. Tap
   **Stop running** to quit early.
7. Daily Doubles come up when the clue was a real Daily Double on the show.
8. Tap **Final Jeopardy!** when you're ready to finish the match.

**Undo** reverses the last action if someone taps the wrong button.

On an iPad, use Safari's **Share → Add to Home Screen**. The game then opens full screen, and
Safari is much less likely to clear the stored clue file and stats.

Stats are saved on the device you play on. Use **Stats → Export** now and then to keep a backup.

## Getting the clue file onto a device

The file is `data/jeopardy-clues.json.gz` (about 26 MB). To copy it to an iPad, AirDrop it from
the Mac, choose to save it to Files, then load it in the game. Saving it to Google Drive or
iCloud Drive works too.

## Rebuilding the clue file

```
python3 tools/build_data.py
```

This downloads the dataset maintained at <https://github.com/jwolle1/jeopardy_clue_dataset>
(derived from j-archive.com) into `data/source/` and writes `data/jeopardy-clues.json.gz`.
Delete `data/source/` first to pick up a newer version of the dataset.

Clue values from before November 26, 2001 (when the show doubled its values) are doubled so all
eras score the same way.

**Never commit anything in `data/`.** The clues are the property of Jeopardy Productions, Inc.
The `.gitignore` file keeps the folder out of the repository.

## Testing on a laptop

```
python3 -m http.server 8000
```

Then open <http://localhost:8000>.
