# 🏎️ F1 Race Winner Prediction System

A beginner-friendly Python mini project that predicts a Formula 1 race winner using rule-based scoring logic.

---

## 📁 Folder Structure

```
F1_Predictor/
│
├── main.py          ← Entry point. Runs the program with a menu.
├── predictor.py     ← Core logic: load, score, rank drivers.
├── drivers.csv      ← Input data: driver grid positions & past results.
└── README.md        ← This file.
```

---

## 🚀 How to Run

```bash
python main.py
```

Make sure `drivers.csv` is in the same folder.

---

## 📊 How the Scoring Works

Each driver gets a **prediction score** based on three factors:

| Factor             | Logic                                          | Max Points |
|--------------------|------------------------------------------------|------------|
| Qualifying Position | P1 → 10 pts, P2 → 9 pts, …                   | 10         |
| Previous Race Finish | P1 → 10 pts, P2 → 9 pts, …                  | 10         |
| Podium Form Bonus  | +5 pts if finished P1–P3 in last race          | 5          |
| Team Strength      | Based on constructor rating (1–10 scale)       | 10         |

**Highest total score = Predicted Winner**

---

## 📝 CSV Format

```csv
Driver,Team,Qualifying,PreviousFinish
Verstappen,Red Bull,1,2
Hamilton,Mercedes,4,3
```

- `Qualifying` — starting grid position (1 = pole)
- `PreviousFinish` — finishing position in the last race (1 = win)

---

## 💡 Features

- ✅ Menu-driven terminal interface
- ✅ Full driver rankings table
- ✅ Score breakdown per driver
- ✅ Modular code (split across files)
- ✅ Clean comments throughout

---

## 🔮 Future Upgrades (Planned)

- [ ] Save prediction history to a file
- [ ] Add weather and track-specific factors
- [ ] Multiple race support
- [ ] Use real data from FastF1 API
- [ ] Basic ML model (Decision Tree)
- [ ] Streamlit web dashboard

---

## 🛠️ Tech Stack

- Python 3.x
- `csv` module (built-in)
- No external dependencies for current version

---

## 📚 Resources

- [FastF1 Documentation](https://docs.fastf1.dev/)
- [FastF1 GitHub](https://github.com/theOehrly/Fast-F1)
