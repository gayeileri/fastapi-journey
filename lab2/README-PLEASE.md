# SFWE477 — Backend Development Labs 🚀

Welcome to the lab repository for **SFWE477: Backend Development with FastAPI**.  
Each lab folder contains practice files — read the comments inside each `.py` file carefully, they contain everything you need to know.

---

## 📁 Repository Setup

1. Create a GitHub account if you don't have one
2. Create a new **public** repository and name it **`fastapi-journey`**
3. Clone it to your machine:
   ```bash
   git clone https://github.com/<your-username>/fastapi-journey.git
   ```
4. Download the lab folder from Moodle, place it inside your repo, and you're ready

---


## 🌿 Branch Naming Policy

Each lab must be worked on its **own branch**. Branch names follow this format:

```
firstinitial+surname-lab2
firstinitial+surname-lab2
```

Use the **first letter of your first name** followed by your **surname** — no spaces, all lowercase.

**Example:** John Snow → `jsnow-lab2` · `jsnow-lab2`

> ⚠️ Do not work on the `main` branch. Do not use spaces or capital letters in branch names.

To create and switch to your branch:
```bash
git checkout -b jsnow-lab2
```

---

## 💾 How to Commit — One Practice at a Time

After you finish **each practice**, stage and commit that file on its own. Do not commit everything at the end.

```bash
# After finishing practice1.py
git add lab2/practice1.py
git commit -m "lab2: complete practice 1"

# After finishing practice2.py
git add lab2/practice2.py
git commit -m "lab2: complete practice 2"

# After finishing practice3.py
git add lab2/practice3.py
git commit -m "lab2: complete practice 3"

# After finishing practice4.py
git add lab2/practice4.py
git commit -m "lab2: complete practice 4"
```

When you are done with all practices, push your branch:
```bash
git push origin jsnow-lab2
```

---

## 📬 Submission

Once your branch is pushed, copy the URL of your branch from GitHub and submit it on Moodle.

The link should look like this:
```
https://github.com/<your-username>/<repo-name>/tree/jsnow-lab2
```


---

## 🎯 Grading

This is a **Pass or Fail** assignment — you either receive the **full grade or nothing**. There is no partial credit.

### ✅ To pass, all three criteria must be met:

| # | Criteria | Details |
|---|----------|---------|
| 1 | **All TODOs completed** | Every `# TODO` in every practice file must be fully implemented and working |
| 2 | **Correct branch & commits** | Branch must follow the `jsnow-lab2` naming format, and each practice must have its own separate commit |
| 3 | **No AI-generated code** | Code must be written by you. AI-assisted submissions will result in a zero and be reported |

### ❌ You will automatically fail if:
- Any TODO is left incomplete or unchanged
- All practices are committed in a single commit
- The branch is incorrectly named or missing
- The submission link is not provided on Moodle before the deadline

### ⏰ Deadline
Late submissions are **not accepted** under any circumstances. A missing Moodle submission by the deadline counts as a zero — no exceptions.

---

*SFWE477 · Final International University*