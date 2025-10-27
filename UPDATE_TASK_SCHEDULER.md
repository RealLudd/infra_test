# 🔧 Update Task Scheduler - Remove Black Window

## Problem
The task runs every 20 seconds, but a black command window flashes briefly.

## Solution
Use `run_invisible.vbs` instead of `run_task.bat` in Task Scheduler!

---

## 📋 How to Update (2 Minutes)

### Step 1: Open Your Scheduled Task
1. Press `Win + R`
2. Type: `taskschd.msc`
3. Press Enter
4. Find your task: **"BPA Monitor"** (or whatever you named it)

### Step 2: Update the Action
1. Right-click your task → **Properties**
2. Go to **Actions** tab
3. Select the action → Click **Edit**
4. Change the program/script from:
   - ❌ Old: `run_task.bat`
   - ✅ New: `run_invisible.vbs`
5. Make sure "Start in" is still: `C:\Users\SA_DE_RPA\infra_test`
6. Click **OK** → **OK**

### Step 3: Test It
1. Right-click your task → **Run**
2. Watch carefully...
3. **NO BLACK WINDOW!** ✅ Completely invisible!

### Troubleshooting: If It Doesn't Work

If the task fails to run:

1. **Test manually first:**
   - Double-click `run_invisible.vbs` in the folder
   - Should be silent (nothing happens visually)
   
2. **Use debug version to see errors:**
   - Temporarily use `run_invisible_debug.vbs` instead
   - It will show a message box if there's an error
   - Once you see what's wrong, switch back to `run_invisible.vbs`

3. **Check "Start in" path:**
   - Must be the full path: `C:\Users\SA_DE_RPA\infra_test`
   - No quotes needed

4. **Run with highest privileges:**
   - In task properties → General tab
   - Check "Run with highest privileges"

---

## ✨ What Changed?

**Before:**
- `run_task.bat` runs → Black window flashes ⬛
- Even in silent mode, window appears briefly

**After:**
- `run_invisible.vbs` runs → **NOTHING visible!** ✅
- Completely invisible, even when checking for updates
- Only shows popup when `SHOW_MESSAGE = True`

---

## 🎯 Result

✅ **Silent mode:** Truly invisible, no windows at all  
✅ **Active mode:** Only shows the chicken popup when you activate it  
✅ **Perfect stealth:** Runs every 20 seconds without any visual indication  

---

**That's it! Your task is now completely invisible until you activate the message from mobile!** 🎉

