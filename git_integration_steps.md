# Git Integration Guide: Merging Your Work with Teammate's Changes

## Current Situation
- **You**: On branch `dev_paul` with uncommitted changes
- **Teammate**: Committed changes to `main` on new repo
- **Old remote**: `Group_02_Seidel_Rally_Vienna_ACO`
- **New remote**: `Group_02_ACO` (https://github.com/paulhimstedt/Group_02_ACO.git)

## Step-by-Step Solution

### Step 1: Save Your Work (Stash)
```bash
# Save all your uncommitted changes
git add .
git stash push -m "My modeling work - ACO, visualizations, docs"
```

### Step 2: Update Remote URL
```bash
# Change to new repository
git remote set-url origin https://github.com/paulhimstedt/Group_02_ACO.git

# Verify
git remote -v
```

### Step 3: Fetch Latest Changes
```bash
# Get all changes from new repo
git fetch origin

# See what's on main
git log origin/main --oneline -10
```

### Step 4: Switch to Main and Update
```bash
# Switch to main branch
git checkout main

# Pull latest changes from teammate
git pull origin main
```

### Step 5: Merge Your Work
```bash
# Create a new branch for merging
git checkout -b merge-modeling-work

# Apply your stashed changes
git stash pop
```

### Step 6: Review and Commit
```bash
# Check what changed
git status

# Review files
git diff

# Add your changes
git add .

# Commit
git commit -m "Add modeling: ACO, Greedy algorithms, visualizations, and documentation"
```

### Step 7: Push and Create Pull Request
```bash
# Push your branch
git push -u origin merge-modeling-work

# Then create PR on GitHub
```

---

## Quick Version (Copy-Paste)

```bash
# 1. Save your work
git add .
git stash push -m "Modeling work"

# 2. Update remote
git remote set-url origin https://github.com/paulhimstedt/Group_02_ACO.git

# 3. Get latest
git fetch origin
git checkout main
git pull origin main

# 4. Merge your work
git checkout -b merge-modeling-work
git stash pop

# 5. Commit
git add .
git commit -m "Add modeling: ACO, Greedy algorithms, visualizations, and documentation"

# 6. Push
git push -u origin merge-modeling-work
```

---

## Alternative: Direct Merge to Main (If You Have Permissions)

```bash
# 1-4. Same as above (stash, update remote, fetch, update main)

# 5. Apply your work directly to main
git checkout main
git stash pop

# 6. Commit and push
git add .
git commit -m "Add modeling: ACO, Greedy algorithms, visualizations, and documentation"
git push origin main
```

---

## Handling Merge Conflicts

If conflicts occur when applying stash:

```bash
# See conflicted files
git status

# For each conflict:
# 1. Open file in VSCode
# 2. Resolve conflicts (choose your version, teammate's, or combine)
# 3. Remove conflict markers (<<<<, ====, >>>>)
# 4. Save file

# Mark as resolved
git add <conflicted-file>

# Continue
git stash drop  # Remove the stash after resolving
```

---

## What Your Teammate Added

Check what's on main:
```bash
git checkout main
git log --oneline -10
ls -la data/real/
```

---

## Recommended Approach

**Option 1: Pull Request (Safer)**
- Create branch `merge-modeling-work`
- Push and create PR
- Teammate reviews
- Merge when approved

**Option 2: Direct Push (If coordinated)**
- Merge directly to main
- Good if teammate is not working right now
- Communicate first!

---

## Checking File Overlap

Before merging, see if there are conflicts:

```bash
# After fetching and checking out main
git checkout main
ls -R  # See what teammate added

# Compare with your stash
git stash show -p  # See your changes
```

Common scenarios:
- **No overlap**: Easy merge, no conflicts
- **Different files**: Auto-merge works
- **Same files modified**: Need manual merge

---

## Pro Tips

1. **Communicate**: Tell teammate you're merging now
2. **Review first**: Check what's on main before merging
3. **Test after merge**: Run `poetry install` and test
4. **Small commits**: If many changes, split into multiple commits

---

## What to Do Right Now

```bash
# Execute these commands:
cd /Users/paulhimstedt/Documents/TU_MASTER/self_organizing_systems/Group_02_Seidel_Rally_Vienna_ACO

# Save your work
git add .
git stash push -m "ACO modeling, visualizations, and documentation"

# Update remote
git remote set-url origin https://github.com/paulhimstedt/Group_02_ACO.git

# Get latest
git fetch origin
git checkout main
git pull origin main

# Check what teammate added
ls -la
ls -la data/real/ 2>/dev/null || echo "No data/real/ yet"

# Create merge branch
git checkout -b merge-modeling-work

# Apply your work
git stash pop

# Now review and commit
```

