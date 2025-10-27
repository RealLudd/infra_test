# 📅 Windows Task Scheduler Setup Guide

## Quick Start: Run Automated Tasks with Mobile Editing

This guide shows how to schedule `run_task.bat` to run automatically, then edit the code from your phone!

---

## 📁 Files Created

1. **`daily_task.py`** - The Python script (edit this from mobile!)
2. **`run_task.bat`** - Batch file that pulls code and runs script
3. **This guide** - Setup instructions

---

## ⚡ Quick Test First!

Before scheduling, test the batch file manually:

1. **Double-click** `run_task.bat`
2. You should see:
   - Git pulling latest code
   - Python script running
   - Messages printed to console

**If it works**, proceed to scheduling! ✅

---

## 🔧 Task Scheduler Setup

### Step 1: Open Task Scheduler

**Option A:** Press `Win + R`, type `taskschd.msc`, press Enter

**Option B:** Search for "Task Scheduler" in Start Menu

### Step 2: Create New Task

1. Click **"Create Basic Task..."** in the right panel
2. Name: `Automated Task Runner`
3. Description: `Pulls code from GitHub and runs daily_task.py`
4. Click **Next**

### Step 3: Set Trigger (When to Run)

Choose your schedule:

**Option 1: Daily**
- Select "Daily"
- Set time (e.g., 9:00 AM)
- Click Next

**Option 2: On Startup**
- Select "When the computer starts"
- Click Next

**Option 3: Every X Minutes**
- Select "Daily"
- After creating, edit the trigger:
  - Open task → Triggers tab → Edit
  - Check "Repeat task every: 30 minutes"
  - Duration: Indefinitely

**Option 4: On Login**
- Select "When I log on"
- Click Next

### Step 4: Set Action

1. Select **"Start a program"**
2. Click **Next**
3. Program/script: Click **Browse**
4. Navigate to your project folder
5. Select **`run_task.bat`**
6. **Start in:** Enter the full path to your project folder
   - Example: `C:\Users\SA_DE_RPA\infra_test`
7. Click **Next**

### Step 5: Finish Setup

1. Review settings
2. Check **"Open the Properties dialog..."**
3. Click **Finish**

### Step 6: Advanced Settings (Optional but Recommended)

In the Properties dialog:

**General Tab:**
- ✅ Check "Run whether user is logged on or not"
- ✅ Check "Run with highest privileges"

**Conditions Tab:**
- ⬜ Uncheck "Start only if on AC power" (if laptop)

**Settings Tab:**
- ✅ Check "Run task as soon as possible after scheduled start is missed"
- ✅ Check "If task fails, restart every: 1 minute"
- Set "Attempt to restart up to: 3 times"

Click **OK** to save

---

## 🧪 Test the Scheduled Task

### Manual Test:
1. Find your task in Task Scheduler
2. Right-click → **Run**
3. Check if it executes successfully

### Check Output:
1. Right-click task → **Properties**
2. Go to **History** tab (enable if needed)
3. See execution results

---

## 📱 Now Test Mobile Editing!

### Step 1: On Claude Mobile

Ask Claude:
```
Change the print message in daily_task.py to say 
"Hello from mobile! Updated at [current time]"
```

### Step 2: Approve Changes

Claude commits → GitHub ✅

### Step 3: Wait for Next Run

The Task Scheduler will:
1. Run `run_task.bat`
2. Pull latest code from GitHub
3. Run `daily_task.py` with **NEW messages!**

### Or Test Immediately:

Right-click task → **Run**

**Check the output - new message appears!** 🎉

---

## 📝 Example Edits from Mobile

Try asking Claude:

1. **"Add a timestamp to each print statement in daily_task.py"**
2. **"Change the message to include a joke"**
3. **"Add a counter that shows how many times this ran"**
4. **"Make it print the current weather"**
5. **"Add an email notification when task completes"**

---

## 🔍 Viewing Logs

### Option 1: Output to File

Modify `run_task.bat` to save output:

```batch
python daily_task.py >> task_output.log 2>&1
```

### Option 2: Windows Event Log

Task Scheduler logs all executions:
- Open Task Scheduler
- Select your task
- Click **History** tab

---

## ⏰ Common Schedules

### Run Every Hour:
- Daily trigger
- Start: 00:00
- Repeat every: 1 hour
- Duration: 1 day

### Run Every 30 Minutes:
- Daily trigger
- Start: 00:00
- Repeat every: 30 minutes
- Duration: 1 day

### Run on Weekdays at 9 AM:
- Weekly trigger
- Days: Mon, Tue, Wed, Thu, Fri
- Start time: 09:00

### Run at Startup:
- Trigger: "At startup"
- Delay: 1 minute (optional)

---

## 🚨 Troubleshooting

### Task Won't Run
- ✅ Check Python is in PATH: `python --version`
- ✅ Check Git is installed: `git --version`
- ✅ Verify "Start in" path is correct
- ✅ Run batch file manually first

### Git Pull Fails
- ✅ Check internet connection
- ✅ Run `git pull` manually in project folder
- ✅ Check GitHub credentials are saved

### Python Script Errors
- ✅ Test script manually: `python daily_task.py`
- ✅ Check Python dependencies installed
- ✅ Review error messages in History tab

### Task Runs but No Output
- ✅ Add output redirection to .bat file
- ✅ Check Task History for errors
- ✅ Verify script is actually running

---

## 🎯 Pro Tips

1. **Test manually first** - Always double-click `run_task.bat` before scheduling
2. **Start simple** - Begin with a long interval (e.g., daily)
3. **Check History** - Enable History tab to see what happened
4. **Use logging** - Add output redirection: `>> log.txt`
5. **Set email alerts** - Configure task to email on failure
6. **Test mobile edits** - Make a small change via Claude to verify workflow

---

## 📊 Workflow Summary

```
📅 Task Scheduler runs → 
   📄 run_task.bat → 
      🔄 git pull (gets latest code) → 
         🐍 python daily_task.py (runs NEW code!)
```

**Edit from mobile:**
```
📱 Claude Mobile → 
   🐙 GitHub → 
      ⏰ Next scheduled run → 
         ✨ New code executes!
```

---

## ✅ You're All Set!

Now you can:
- ✅ Schedule tasks to run automatically
- ✅ Edit code from anywhere via mobile
- ✅ Changes apply on next run
- ✅ No remote desktop needed!

**Test it now:**
1. Set up Task Scheduler (5 minutes)
2. Run task manually to verify
3. Edit `daily_task.py` from Claude mobile
4. Run task again → See new message! 🎉

---

**Ready to automate everything? 🚀**

