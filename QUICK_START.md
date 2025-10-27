# 🚀 BPA Quick Start Guide

## How It Works

This script runs **silently every 20 seconds** in the background. It only shows a popup when you activate it from your mobile!

---

## ⚙️ Setup Task Scheduler (One Time)

### 1. Open Task Scheduler
- Press `Win + R`
- Type: `taskschd.msc`
- Press Enter

### 2. Create New Task
- Click **"Create Basic Task..."**
- Name: `BPA Monitor`
- Description: `Runs every 20 seconds, shows popup when activated from mobile`

### 3. Set Trigger
- Select **"Daily"**
- Start: Today at **00:00**
- Click **Next**

### 4. Set Action
- Select **"Start a program"**
- Browse to: `run_invisible.vbs` (in this folder) ← **Use THIS, not .bat!**
- **Important:** "Start in" = `C:\Users\SA_DE_RPA\infra_test`
- Click **Next** → **Finish**

**Note:** Using `run_invisible.vbs` instead of `run_task.bat` ensures **NO BLACK WINDOW** appears at all!

### 5. Configure Repeat Interval
- Right-click your task → **Properties**
- Go to **Triggers** tab
- Click **Edit**
- Check **"Repeat task every"**
- Select: **5 minutes** (or custom: 20 seconds*)
- Duration: **Indefinitely**
- Click **OK**

*For custom 20 seconds: After saving, edit the XML directly or use PowerShell

### 6. Advanced Settings (Optional)
- **General** tab:
  - ✅ "Run whether user is logged on or not"
  - ✅ "Run with highest privileges"
- **Settings** tab:
  - ✅ "Run task as soon as possible after scheduled start is missed"
  - ✅ "If the running task does not end when requested, force it to stop"

---

## 📱 How to Use from Mobile

### To Show a Popup:

On **Claude mobile**, say:

```
In daily_task.py, change SHOW_MESSAGE from False to True
```

**What happens:**
- Next run (within 20 seconds) → Popup appears! 🎉
- Shows your message with chicken art
- Countdown 10...9...8...
- Window closes automatically

---

### To Hide the Popup Again:

On **Claude mobile**, say:

```
In daily_task.py, change SHOW_MESSAGE from True to False
```

**What happens:**
- Next run → Goes silent again
- Runs in background every 20 seconds
- No popup, no window

---

### To Change the Message:

On **Claude mobile**, say:

```
In daily_task.py, change the message to "Your new message here!"
```

**Example:**
```
Change the message in daily_task.py to 
"Alert: Important update from Marco!"
```

---

## 🎯 Example Workflow

### Scenario: Send yourself a reminder

**1. From mobile (Claude):**
```
In daily_task.py:
1. Change SHOW_MESSAGE to True
2. Change the message to "Time for your 3pm meeting!"
```

**2. Wait 20 seconds:**
- Popup appears on your computer! 🎉
- Shows the reminder with chicken art
- Auto-closes after 10 seconds

**3. Turn it off (from mobile):**
```
In daily_task.py, change SHOW_MESSAGE to False
```

**4. Next run:**
- Goes silent again
- Waits for your next activation

---

## 💡 Use Cases

### 1. Quick Reminders
- Activate popup from mobile
- Reminds you on your computer
- Turn off when done

### 2. Status Notifications
- Change message from mobile
- Shows status on your workstation
- Disable when not needed

### 3. Alert System
- Runs silently in background
- Activate when you need to alert yourself
- Auto-disables after viewing

### 4. Team Communication
- Send messages to your workstation from anywhere
- No need for chat apps
- Direct popup on screen

---

## 🔧 Customization

### Change Countdown Time

In `daily_task.py`, find:
```python
countdown(10)  # Change 10 to your desired seconds
```

### Change Schedule Interval

In Task Scheduler:
- Right-click task → Properties
- Triggers → Edit
- Change "Repeat task every" interval

### Change Message Position or Style

Edit the `print_header()` and print statements in `daily_task.py`

---

## 🚨 Troubleshooting

### Popup not showing
- Check Task Scheduler: Is it running?
- Check `SHOW_MESSAGE` = `True` in `daily_task.py`
- Run manually: Double-click `run_task.bat`

### Too many popups
- Set `SHOW_MESSAGE = False` from mobile
- Or disable the scheduled task temporarily

### Want to test immediately
- Double-click `run_task.bat`
- Or right-click task in scheduler → **Run**

---

## 📊 Current Status

**Default State:** `SHOW_MESSAGE = False` (Silent)

**To activate:**
- Edit from Claude mobile
- Change to `True`
- Popup appears within 20 seconds!

**To deactivate:**
- Edit from Claude mobile
- Change to `False`
- Goes silent again

---

## ✅ Quick Commands for Claude Mobile

### Show popup:
```
Change SHOW_MESSAGE to True in daily_task.py
```

### Hide popup:
```
Change SHOW_MESSAGE to False in daily_task.py
```

### Change message:
```
In daily_task.py, change the message to "[your message]"
```

### Both at once:
```
In daily_task.py:
- Change SHOW_MESSAGE to True
- Change the message to "Time for lunch!"
```

---

**🎉 That's it! Your BPA monitor is ready to go!**

Just schedule it in Task Scheduler and control it from your mobile! 🚀

