import json
import os
import sys
import re


def _get_user_kb_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.expanduser("~"), ".yakety-yak", "knowledge_base.json")
    return "terminal_knowledge_base.json"


DEFAULT_KB_PATH = _get_user_kb_path()

DEFAULT_KNOWLEDGE_BASE = {
    "commands": {
        "ls": {
            "beginner": "This command lists all the files and folders in your current directory (like opening a folder on your desktop to see what's inside). Common flags: -l (detailed list), -a (show hidden files), -h (human-readable sizes).",
            "familiar": "Lists directory contents. Common flags: -l (long format), -a (show hidden), -h (human-readable sizes)."
        },
        "cd": {
            "beginner": "This command changes which folder you're currently working in. Think of it like double-clicking a folder to go inside it. 'cd ..' goes back up one level, 'cd ~' goes to your home folder.",
            "familiar": "Change directory. Use 'cd ..' to go up, 'cd ~' for home, 'cd -' for previous directory."
        },
        "pwd": {
            "beginner": "This shows you the full path of the folder you're currently in. It's like looking at the address bar in a file explorer to see where you are.",
            "familiar": "Print working directory \u2014 shows the absolute path of your current location."
        },
        "mkdir": {
            "beginner": "This creates a new folder. For example, 'mkdir my_project' makes a new folder called 'my_project'. Use -p to create nested folders.",
            "familiar": "Create a new directory. Use -p to create nested directories (e.g., mkdir -p a/b/c)."
        },
        "rm": {
            "beginner": "This deletes a file permanently (it does NOT go to the trash!). Be very careful! 'rm -r' deletes entire folders and everything inside them. 'rm -f' forces deletion without asking.",
            "familiar": "Remove files/directories. -r for recursive, -f for force (no confirmation). Use with caution."
        },
        "cp": {
            "beginner": "This copies a file from one place to another. For example, 'cp file.txt backup.txt' makes a copy of file.txt called backup.txt. Use -r to copy entire folders.",
            "familiar": "Copy files/directories. Use -r for directories, -i for interactive (confirm overwrite)."
        },
        "mv": {
            "beginner": "This moves a file to a different location OR renames it. 'mv old_name.txt new_name.txt' renames the file. 'mv file.txt /other/folder/' moves it.",
            "familiar": "Move or rename files/directories. Also used for renaming in-place."
        },
        "cat": {
            "beginner": "This displays the entire contents of a file right in your terminal, like opening a text file to read it. For large files, use 'less' instead.",
            "familiar": "Concatenate and display file contents. For large files, consider using 'less' or 'head'/'tail' instead."
        },
        "grep": {
            "beginner": "This searches through files to find lines that contain specific text. It's like using Ctrl+F (Find) but for files in your terminal. Example: 'grep error log.txt' finds all lines with 'error'.",
            "familiar": "Search text using patterns. -r for recursive, -i for case-insensitive, -n for line numbers, -E for extended regex."
        },
        "chmod": {
            "beginner": "This changes who can read, write, or run a file. For example, 'chmod +x script.sh' makes a file executable (so you can run it as a program).",
            "familiar": "Change file permissions. Octal (755) or symbolic (+x, u+rw) notation. Common: 755 (rwxr-xr-x), 644 (rw-r--r--)."
        },
        "sudo": {
            "beginner": "This runs a command with administrator (superuser) privileges. It's like right-clicking 'Run as Administrator' on Windows. You'll need to enter your password.",
            "familiar": "Execute command as superuser. Use sparingly. 'sudo !!' repeats last command with sudo."
        },
        "pip install": {
            "beginner": "This downloads and installs a Python package (a pre-built tool or library) from the internet so you can use it in your code.",
            "familiar": "Install Python packages from PyPI. Use -r requirements.txt for bulk install, --upgrade to update."
        },
        "pip": {
            "beginner": "Pip is Python's package installer. It lets you download and manage libraries and tools. 'pip install <name>' adds a package, 'pip list' shows installed ones.",
            "familiar": "Python package manager. install, uninstall, list, freeze, show. Use pip3 on systems with both Python 2 and 3."
        },
        "npm install": {
            "beginner": "This downloads and installs a JavaScript/Node.js package so you can use it in your project. It saves it in a folder called 'node_modules'.",
            "familiar": "Install Node.js packages. --save-dev for dev dependencies, -g for global install."
        },
        "npm": {
            "beginner": "npm is the Node.js package manager. It lets you install JavaScript libraries, run scripts, and manage your project. 'npm install' gets all dependencies, 'npm run' runs scripts.",
            "familiar": "Node.js package manager. install, run, test, build, publish. See package.json for available scripts."
        },
        "git clone": {
            "beginner": "This downloads a complete copy of a project from the internet (usually from GitHub) to your computer so you can work on it.",
            "familiar": "Clone a remote repository. Use --depth 1 for shallow clone, --branch to specify branch."
        },
        "git add": {
            "beginner": "This tells Git to start tracking changes you've made to specific files. It's like putting files in a 'ready to save' staging area before committing.",
            "familiar": "Stage changes for commit. 'git add .' stages all, 'git add -p' for interactive staging."
        },
        "git commit": {
            "beginner": "This saves a snapshot of all your staged changes with a descriptive message. Think of it as creating a save point you can return to later.",
            "familiar": "Record staged changes. -m for inline message, --amend to modify last commit."
        },
        "git push": {
            "beginner": "This uploads your saved changes (commits) to a remote server like GitHub so others can see and use your work.",
            "familiar": "Upload local commits to remote. -u to set upstream, --force to overwrite (use carefully)."
        },
        "git pull": {
            "beginner": "This downloads the latest changes from the remote server and merges them into your local copy of the project.",
            "familiar": "Fetch and merge remote changes. --rebase to rebase instead of merge."
        },
        "git status": {
            "beginner": "This shows you which files have been changed, which are staged (ready to commit), and which are not being tracked by Git. Very useful to see what's going on.",
            "familiar": "Show working tree status. -s for short format, --branch for branch info."
        },
        "git diff": {
            "beginner": "This shows you exactly what changes you've made to files since the last commit. Added lines show in green with '+', removed lines in red with '-'.",
            "familiar": "Show changes between commits, working tree, etc. --staged for staged changes, --stat for summary."
        },
        "git log": {
            "beginner": "This shows the history of all previous commits (save points) in your project, with who made them and when.",
            "familiar": "Show commit history. --oneline for compact view, --graph for branch visualization, -n to limit count."
        },
        "git branch": {
            "beginner": "This shows or creates branches. Branches let you work on different features without affecting the main code. Like having parallel copies of your project.",
            "familiar": "List, create, or delete branches. -d to delete, -a to show all (including remote)."
        },
        "git checkout": {
            "beginner": "This switches between branches or restores files. 'git checkout main' switches to the main branch. 'git checkout -b new-branch' creates and switches to a new branch.",
            "familiar": "Switch branches or restore files. -b to create and switch. Prefer 'git switch' for branch switching."
        },
        "python": {
            "beginner": "This runs a Python script or starts the Python interactive mode where you can type Python code and see results immediately.",
            "familiar": "Run Python interpreter or script. -m to run a module, -c for inline command, -i for interactive after script."
        },
        "node": {
            "beginner": "This runs JavaScript code outside of a web browser using Node.js. You can run a .js file or start an interactive JavaScript console.",
            "familiar": "Run Node.js scripts or REPL. --inspect for debugging, --experimental-modules for ESM."
        },
        "curl": {
            "beginner": "This downloads data from a URL or sends data to a web server, right from your terminal. It's often used to test if websites or APIs are working.",
            "familiar": "Transfer data via URLs. -X for method, -H for headers, -d for data, -o to save output, -v for verbose."
        },
        "ssh": {
            "beginner": "This lets you securely connect to and control another computer over the internet, as if you were sitting right in front of it.",
            "familiar": "Secure shell connection. -i for identity file, -p for port, -L for local port forwarding."
        },
        "docker": {
            "beginner": "Docker manages lightweight virtual computers called 'containers' that package up your app and everything it needs to run, so it works the same everywhere.",
            "familiar": "Container management. Common: run, build, ps, logs, exec, stop, rm. Use docker-compose for multi-container setups."
        },
        "echo": {
            "beginner": "This prints text to the terminal. It's often used in scripts to show messages or to write text into files using > or >>.",
            "familiar": "Output text to terminal. Use with >> to append to files, > to overwrite. Supports variable expansion."
        },
        "touch": {
            "beginner": "This creates a new empty file, or if the file already exists, updates its 'last modified' timestamp.",
            "familiar": "Create empty files or update timestamps. Commonly used for quick file creation."
        },
        "find": {
            "beginner": "This searches your computer for files and folders matching certain criteria, like name, size, or when they were modified.",
            "familiar": "Search for files in directory tree. -name for name pattern, -type f/d for files/dirs, -exec to run commands on results."
        },
        "kill": {
            "beginner": "This stops a running program by sending it a signal. You need to know the program's process ID (PID), which you can find using 'ps' or 'top'.",
            "familiar": "Send signals to processes. -9 for SIGKILL (force), -15 for SIGTERM (graceful). Use killall for name-based."
        },
        "ps": {
            "beginner": "This shows a list of programs currently running on your computer. 'ps aux' shows all processes. Useful to find the ID of a process you want to stop.",
            "familiar": "List running processes. aux for all users, -ef for full format. Pipe to grep to filter."
        },
        "top": {
            "beginner": "This shows you a live updating list of all running programs and how much of your computer's resources (CPU, memory) they're using. Press 'q' to quit.",
            "familiar": "Real-time process monitor. Press 'q' to quit, 'M' to sort by memory, 'P' by CPU. Consider using htop."
        },
        "man": {
            "beginner": "This opens the manual (help documentation) for any command. For example, 'man ls' shows you everything you can do with the 'ls' command. Press 'q' to quit.",
            "familiar": "Display manual pages. Use 'q' to exit, '/' to search, 'n' for next match."
        },
        "tar": {
            "beginner": "This packs multiple files and folders into a single archive file (like creating a .zip file). It's often used with compression to make files smaller.",
            "familiar": "Archive utility. -czf to create gzipped, -xzf to extract gzipped, -tf to list contents."
        },
        "wget": {
            "beginner": "This downloads files from the internet. You give it a URL and it saves the file to your current folder.",
            "familiar": "Download files from URLs. -O for output filename, -r for recursive, -c to resume, -q for quiet."
        },
        "apt": {
            "beginner": "This is the package manager for Ubuntu/Debian Linux. It lets you install, update, and remove software on your system (like an app store for the terminal).",
            "familiar": "Debian package manager. install, remove, update (refresh list), upgrade (install updates), autoremove, search."
        },
        "brew": {
            "beginner": "Homebrew is a package manager for macOS (and Linux). It lets you easily install software and developer tools that aren't included with your operating system.",
            "familiar": "macOS/Linux package manager. install, uninstall, update, upgrade, search, info, list."
        },
        "head": {
            "beginner": "This shows only the first few lines of a file (10 by default). Useful for peeking at large files without loading everything.",
            "familiar": "Show first N lines of a file. -n to specify count. Default is 10 lines."
        },
        "tail": {
            "beginner": "This shows the last few lines of a file (10 by default). Very useful for checking recent log entries. 'tail -f' watches a file for new lines in real-time.",
            "familiar": "Show last N lines. -n for count, -f to follow (live updates). Great for log monitoring."
        },
        "wc": {
            "beginner": "This counts the number of lines, words, and characters in a file. 'wc -l' counts just lines.",
            "familiar": "Word/line/char count. -l lines only, -w words only, -c bytes, -m characters."
        },
        "which": {
            "beginner": "This tells you where a program is installed on your computer. For example, 'which python' shows the full path to the Python executable.",
            "familiar": "Locate a command's executable path. Useful for debugging PATH issues."
        },
        "env": {
            "beginner": "This shows all the environment variables set in your terminal session. Environment variables are like settings that programs can read.",
            "familiar": "Display or set environment variables. Often piped to grep: env | grep PATH."
        },
        "export": {
            "beginner": "This sets an environment variable that other programs can use. For example, 'export API_KEY=abc123' stores a value that your app can read.",
            "familiar": "Set environment variables for the current session. Add to ~/.bashrc or ~/.zshrc for persistence."
        },
        "source": {
            "beginner": "This runs all the commands in a file within your current terminal session. Commonly used to activate virtual environments or reload config files.",
            "familiar": "Execute file in current shell context. Common: source ~/.bashrc, source venv/bin/activate."
        },
        "clear": {
            "beginner": "This clears all the text from your terminal screen, giving you a fresh, clean view. Your command history is still there, just scrolled away.",
            "familiar": "Clear terminal screen. Ctrl+L is a common shortcut alternative."
        },
        "history": {
            "beginner": "This shows a list of all the commands you've typed recently. You can re-run a previous command by typing '!' followed by its number.",
            "familiar": "Show command history. !n to re-run command n, !! for last command, !string for last command starting with string."
        },
        "date": {
            "beginner": "This shows the current date and time on your computer. You can also use it to display dates in different formats.",
            "familiar": "Display or set system date/time. Use +FORMAT for custom output (e.g., date '+%Y-%m-%d')."
        },
        "whoami": {
            "beginner": "This shows your current username \u2014 the name your computer knows you by. Useful when you're not sure which account you're logged into.",
            "familiar": "Print effective user ID / username."
        },
        "uname": {
            "beginner": "This shows information about your operating system. 'uname -a' shows everything: OS name, version, computer type, and more.",
            "familiar": "Print system info. -a for all, -s for OS name, -r for kernel release, -m for machine type."
        },
        "df": {
            "beginner": "This shows how much disk space you have available on your computer. 'df -h' makes the numbers easy to read (like '50G' instead of a huge number).",
            "familiar": "Report filesystem disk space usage. -h for human-readable, -i for inodes, -T for filesystem type."
        },
        "free": {
            "beginner": "This shows how much memory (RAM) your computer has and how much is being used. 'free -h' makes it easy to read.",
            "familiar": "Display memory usage. -h for human-readable, -g for gigabytes, -s N for continuous monitoring every N seconds."
        },
        "uptime": {
            "beginner": "This shows how long your computer has been running since it was last turned on, plus the system load (how busy it is).",
            "familiar": "Show system uptime and load averages (1, 5, 15 min). Load > number of CPUs indicates saturation."
        },
        "less": {
            "beginner": "This lets you scroll through a file page by page (unlike 'cat' which dumps everything at once). Press 'q' to quit, arrow keys to scroll, '/' to search.",
            "familiar": "Pager for viewing files. q to quit, / to search, n/N for next/prev match, g/G for top/bottom."
        },
        "sort": {
            "beginner": "This arranges lines of text in order (alphabetically by default). 'sort -n' sorts by number, 'sort -r' sorts in reverse.",
            "familiar": "Sort lines of text. -n for numeric, -r for reverse, -k for key field, -u for unique, -t for delimiter."
        },
        "uniq": {
            "beginner": "This removes duplicate lines that are next to each other. Usually used after 'sort' to get only unique lines.",
            "familiar": "Filter adjacent duplicate lines. -c for count, -d to show only duplicates, -u for unique only. Requires sorted input."
        },
        "sed": {
            "beginner": "This is a text editor that works on streams of text (not interactively). It's most commonly used to find and replace text in files, like 'sed s/old/new/g file.txt'.",
            "familiar": "Stream editor. Common: s/pattern/replacement/g for substitution, -i for in-place edit, -E for extended regex."
        },
        "awk": {
            "beginner": "This is a powerful text-processing tool that works on columns of data. It can pick out specific columns, do math, and filter lines.",
            "familiar": "Pattern scanning and processing. '{print $1}' for first column, -F for delimiter, supports conditions and functions."
        },
        "xargs": {
            "beginner": "This takes a list of items (usually from another command) and runs a command on each one. It's like a 'for each' loop in the terminal.",
            "familiar": "Build and execute commands from stdin. -I{} for placeholder, -P for parallel, -n for max args per command."
        },
        "tee": {
            "beginner": "This sends output to both the screen AND a file at the same time. Useful when you want to see output and save it too.",
            "familiar": "Read stdin and write to both stdout and files. -a to append instead of overwrite."
        },
        "diff": {
            "beginner": "This compares two files and shows you exactly what's different between them. Lines with '<' are from the first file, '>' from the second.",
            "familiar": "Compare files line by line. -u for unified format, -r for recursive (directories), --color for colored output."
        },
        "ln": {
            "beginner": "This creates a link (shortcut) to a file or folder. 'ln -s target linkname' creates a symbolic link, like a shortcut on your desktop.",
            "familiar": "Create hard or symbolic links. -s for symbolic (soft) link, -f to force overwrite. Symlinks are more common."
        },
        "du": {
            "beginner": "This shows how much disk space files and folders are using. 'du -sh *' gives you a nice summary of each item in the current folder.",
            "familiar": "Estimate file/directory space usage. -s for summary, -h for human-readable, --max-depth=N to limit depth."
        },
        "tree": {
            "beginner": "This shows all the files and folders in a nice tree-like diagram, so you can see the whole structure at a glance.",
            "familiar": "List directory contents in tree format. -L N for depth limit, -a for hidden files, -d for directories only."
        },
        "htop": {
            "beginner": "This is a prettier, more interactive version of 'top'. It shows all running programs and resource usage with color coding. Press 'q' to quit, F9 to kill a process.",
            "familiar": "Interactive process viewer. Better than top. F5 for tree view, F6 to sort, F9 to kill, / to search."
        },
        "nano": {
            "beginner": "This opens a simple text editor right in your terminal. It's the easiest terminal text editor for beginners. The commands are shown at the bottom (^ means Ctrl).",
            "familiar": "Simple terminal text editor. Ctrl+O to save, Ctrl+X to exit, Ctrl+W to search, Ctrl+K to cut line."
        },
        "vim": {
            "beginner": "This is a powerful text editor in your terminal. It can be confusing at first! Press 'i' to start typing, 'Esc' to stop typing, then ':wq' and Enter to save and quit. To quit without saving: ':q!' and Enter.",
            "familiar": "Modal text editor. i for insert mode, Esc for normal mode, :w to save, :q to quit, :wq to save+quit, /pattern to search."
        },
        "ping": {
            "beginner": "This checks if you can reach another computer or website over the internet. It sends small packets and measures how long they take to come back. Press Ctrl+C to stop.",
            "familiar": "Send ICMP echo requests. -c N for count, -i N for interval. Ctrl+C to stop. Useful for connectivity testing."
        },
        "ifconfig": {
            "beginner": "This shows your computer's network connections and IP addresses. It tells you how your computer is connected to networks.",
            "familiar": "Display/configure network interfaces. Deprecated in favor of 'ip addr' on modern Linux."
        },
        "ip": {
            "beginner": "This is the modern way to see and configure your computer's network settings. 'ip addr' shows your IP addresses, 'ip route' shows how traffic flows.",
            "familiar": "Show/manipulate networking. 'ip addr' for addresses, 'ip route' for routing, 'ip link' for interfaces."
        },
        "netstat": {
            "beginner": "This shows all the network connections your computer currently has open. Useful to see what programs are using the network.",
            "familiar": "Network statistics. -tlnp for listening TCP with PIDs, -an for all connections. Consider 'ss' as modern replacement."
        },
        "zip": {
            "beginner": "This compresses files into a .zip archive (like right-clicking and choosing 'Compress' on your desktop). 'unzip' extracts them.",
            "familiar": "Create zip archives. -r for recursive (directories), unzip to extract, -l to list contents."
        },
        "scp": {
            "beginner": "This copies files securely between your computer and another computer over the internet. It works like 'cp' but across machines.",
            "familiar": "Secure copy over SSH. scp file user@host:path for upload, scp user@host:file . for download. -r for directories."
        },
        "crontab": {
            "beginner": "This lets you schedule commands to run automatically at specific times (like setting an alarm). 'crontab -l' shows your scheduled tasks, 'crontab -e' lets you edit them.",
            "familiar": "Manage cron jobs. -l to list, -e to edit, -r to remove. Format: min hour day month weekday command."
        },
        "alias": {
            "beginner": "This creates a shortcut for a longer command. For example, 'alias ll=ls -la' lets you type just 'll' instead of 'ls -la'.",
            "familiar": "Create command shortcuts. Add to ~/.bashrc for persistence. 'unalias' to remove. 'alias' alone lists all."
        },
        "nslookup": {
            "beginner": "This looks up the IP address of a website. For example, 'nslookup google.com' shows you the actual server addresses behind that name.",
            "familiar": "Query DNS records. Alternative: dig. Shows A, AAAA, MX records etc."
        },
        "dig": {
            "beginner": "This queries DNS servers to find information about domain names, like what IP address a website points to. It gives more detailed output than nslookup.",
            "familiar": "DNS lookup utility. +short for concise, +trace for resolution path, @server to query specific DNS server."
        },
        "traceroute": {
            "beginner": "This shows the path your internet traffic takes to reach a destination, listing every router it passes through. Helpful to see where a connection slows down.",
            "familiar": "Trace packet route to host. -n for numeric output, -m for max hops. Use tracepath on some Linux distros."
        },
        "host": {
            "beginner": "This looks up the IP address of a domain name. It's simpler than dig and gives you a quick answer.",
            "familiar": "DNS lookup utility. Shows A, AAAA, MX records. Simpler output than dig."
        },
        "hostname": {
            "beginner": "This shows or sets the name of your computer on the network. Every computer has a hostname to identify itself.",
            "familiar": "Show/set system hostname. -I for IP addresses, -f for FQDN."
        },
        "ss": {
            "beginner": "This shows information about network connections on your computer. It's the modern replacement for netstat and is faster.",
            "familiar": "Socket statistics. -t for TCP, -u for UDP, -l for listening, -n for numeric, -p for process. Modern replacement for netstat."
        },
        "iptables": {
            "beginner": "This is the Linux firewall tool that controls which network traffic is allowed in and out of your computer. It requires administrator access.",
            "familiar": "Firewall management. -L to list rules, -A to append, -D to delete, -P for default policy. Consider nftables or ufw for simpler usage."
        },
        "ufw": {
            "beginner": "This is a simplified firewall tool for Linux. 'ufw enable' turns it on, 'ufw allow 80' opens a port. Much easier than iptables.",
            "familiar": "Uncomplicated Firewall. enable/disable, allow/deny port, status for listing rules. Frontend for iptables."
        },
        "nc": {
            "beginner": "Netcat is a versatile networking tool often called the 'Swiss army knife' of networking. It can send and receive data over network connections.",
            "familiar": "Netcat - network utility. -l for listen, -p for port, -z for scan, -v for verbose. Useful for port scanning and data transfer."
        },
        "tcpdump": {
            "beginner": "This captures and displays network traffic passing through your computer. It's like wiretapping your own network connection to see what data is being sent and received.",
            "familiar": "Packet capture tool. -i for interface, -w to write pcap, -r to read pcap, -n for numeric, port/host filters."
        },
        "nmap": {
            "beginner": "This scans computers and networks to see what services are running and which ports are open. It's used by security professionals to check for vulnerabilities.",
            "familiar": "Network scanner. -sS for SYN scan, -sV for version detection, -O for OS detection, -p for port range, -A for aggressive."
        },
        "rsync": {
            "beginner": "This copies files between locations, but it's smarter than cp \u2014 it only copies files that have changed. Great for backups and syncing folders.",
            "familiar": "Remote/local file sync. -a for archive, -v for verbose, -z for compress, --delete to mirror, --dry-run to preview."
        },
        "lsof": {
            "beginner": "This shows which files are currently open and which programs have them open. 'lsof -i :8080' shows what's using port 8080.",
            "familiar": "List open files. -i for network connections, -p for PID, +D for directory. Essential for port/file debugging."
        },
        "strace": {
            "beginner": "This shows you every system call a program makes as it runs. Useful for debugging when you want to see exactly what a program is doing behind the scenes.",
            "familiar": "Trace system calls. -p for attach to PID, -e for filter calls, -f for follow forks, -o for output file."
        },
        "ltrace": {
            "beginner": "This traces the library function calls that a program makes. Similar to strace but focuses on library calls instead of system calls.",
            "familiar": "Trace library calls. -p for PID, -e for filter, -c for summary. Complements strace for debugging."
        },
        "dmesg": {
            "beginner": "This shows kernel messages \u2014 low-level messages from your operating system about hardware, drivers, and system events. Useful for diagnosing hardware issues.",
            "familiar": "Print kernel ring buffer. -T for timestamps, -w to follow, --level for severity filter."
        },
        "journalctl": {
            "beginner": "This shows the system log entries on Linux systems using systemd. It's the central place to find error messages and system events.",
            "familiar": "Query systemd journal. -u for unit, -f to follow, --since for time filter, -b for current boot, -p for priority."
        },
        "systemctl": {
            "beginner": "This controls system services on Linux. 'systemctl start nginx' starts a service, 'systemctl stop nginx' stops it, 'systemctl status nginx' checks if it's running.",
            "familiar": "Manage systemd services. start/stop/restart/status/enable/disable. list-units for all services, is-active for quick check."
        },
        "service": {
            "beginner": "This starts, stops, or restarts system services. For example, 'service nginx restart' restarts your web server. Older alternative to systemctl.",
            "familiar": "Manage system services (SysV init). start/stop/restart/status. Prefer systemctl on systemd-based systems."
        },
        "chown": {
            "beginner": "This changes who owns a file or folder. For example, 'chown user:group file.txt' sets both the owner and group. Often needed with sudo.",
            "familiar": "Change file owner and group. -R for recursive. Format: chown user:group file. Common when fixing permission issues."
        },
        "chgrp": {
            "beginner": "This changes the group ownership of a file. Groups let multiple users share access to files.",
            "familiar": "Change group ownership. -R for recursive. See 'groups' to list available groups."
        },
        "passwd": {
            "beginner": "This changes your password or another user's password (with sudo). Your computer will ask you to type the old password first, then the new one twice.",
            "familiar": "Change user password. sudo passwd user for other users, -l to lock, -u to unlock account."
        },
        "useradd": {
            "beginner": "This creates a new user account on the system. You need administrator access. Use 'adduser' on Debian/Ubuntu for a friendlier version.",
            "familiar": "Create user account. -m for home directory, -s for shell, -G for groups. Prefer adduser on Debian-based systems."
        },
        "usermod": {
            "beginner": "This modifies an existing user account. You can change their home directory, shell, or add them to groups.",
            "familiar": "Modify user account. -aG to add to group, -s for shell, -d for home directory, -l to rename."
        },
        "userdel": {
            "beginner": "This deletes a user account from the system. Use -r to also remove their home directory and files.",
            "familiar": "Delete user account. -r to remove home directory. Back up user data first."
        },
        "groupadd": {
            "beginner": "This creates a new group on the system. Groups are used to give multiple users shared access to certain files or resources.",
            "familiar": "Create a new group. Use usermod -aG to add users to the group."
        },
        "groups": {
            "beginner": "This shows which groups a user belongs to. Groups control what files and resources you have access to.",
            "familiar": "Print group memberships. 'groups username' for specific user, 'id' for detailed info."
        },
        "id": {
            "beginner": "This shows your user ID, group ID, and all the groups you belong to. It gives you a complete picture of your identity on the system.",
            "familiar": "Print user and group IDs. -u for UID only, -g for GID only, -G for all group IDs."
        },
        "su": {
            "beginner": "This switches to a different user account in the terminal. 'su -' switches to root (administrator). You'll need that user's password.",
            "familiar": "Switch user. su - for login shell (loads user's environment), su -c 'command' to run single command."
        },
        "mount": {
            "beginner": "This attaches a storage device (like a USB drive or hard disk) to your file system so you can access its files.",
            "familiar": "Mount filesystem. -t for type, -o for options (ro, rw, noexec). /etc/fstab for automatic mounting."
        },
        "umount": {
            "beginner": "This safely disconnects a storage device from your computer. Always unmount before physically removing a USB drive.",
            "familiar": "Unmount filesystem. -l for lazy unmount, -f for force. Ensure no processes are using the mount point."
        },
        "fdisk": {
            "beginner": "This manages disk partitions (dividing a disk into separate sections). Be very careful \u2014 wrong changes can destroy data.",
            "familiar": "Partition table manipulator. -l to list partitions. Interactive mode for creating/deleting partitions. Consider gdisk for GPT."
        },
        "mkfs": {
            "beginner": "This formats a disk partition with a filesystem (like preparing a blank notebook for writing). This erases all existing data on the partition.",
            "familiar": "Create filesystem. mkfs.ext4, mkfs.xfs, etc. This is destructive \u2014 all data on the partition will be lost."
        },
        "lsblk": {
            "beginner": "This lists all the storage devices (hard drives, SSDs, USB drives) connected to your computer and how they're organized.",
            "familiar": "List block devices. -f for filesystem info, -o for custom columns. Shows device tree structure."
        },
        "blkid": {
            "beginner": "This shows the unique identifiers (UUIDs) and filesystem types of your storage devices. Useful for configuring automatic mounting.",
            "familiar": "Print block device attributes. Shows UUID, TYPE, LABEL. Used for /etc/fstab configuration."
        },
        "dd": {
            "beginner": "This copies data at a very low level, byte by byte. It can create disk images, bootable USB drives, and more. Be very careful \u2014 it can overwrite your entire disk.",
            "familiar": "Low-level data copy. if=input, of=output, bs=block size, count=blocks. status=progress for progress bar. Extremely dangerous if misused."
        },
        "rsyslog": {
            "beginner": "This is the system logging service that records events and errors from programs running on your Linux system.",
            "familiar": "System logging daemon. Config in /etc/rsyslog.conf. Logs typically stored in /var/log/."
        },
        "logrotate": {
            "beginner": "This automatically manages log files by compressing old ones and deleting very old ones, so they don't fill up your disk.",
            "familiar": "Log file rotation. Config in /etc/logrotate.d/. -f to force rotation, -d for debug/dry-run."
        },
        "watch": {
            "beginner": "This runs a command repeatedly and shows the output, so you can see it change in real time. For example, 'watch -n 2 ls' runs 'ls' every 2 seconds.",
            "familiar": "Execute command periodically. -n for interval, -d to highlight differences. Ctrl+C to stop."
        },
        "screen": {
            "beginner": "This lets you run programs in the background even after you disconnect from a remote server. Your programs keep running and you can reconnect later.",
            "familiar": "Terminal multiplexer. Ctrl+A D to detach, screen -r to reattach, -ls to list sessions. Consider tmux as alternative."
        },
        "tmux": {
            "beginner": "This lets you split your terminal into multiple panes and windows, and keep programs running in the background. Like having multiple terminal tabs on steroids.",
            "familiar": "Terminal multiplexer. Ctrl+B then: % for vertical split, \" for horizontal, c for new window, d to detach, [ for scroll mode."
        },
        "cron": {
            "beginner": "Cron is the system that runs scheduled tasks automatically at set times. Use 'crontab -e' to edit your scheduled tasks.",
            "familiar": "Task scheduler daemon. See crontab for user job management. System jobs in /etc/cron.d/, /etc/cron.daily/, etc."
        },
        "at": {
            "beginner": "This schedules a command to run once at a specific time in the future. Unlike cron, it's for one-time tasks, not recurring ones.",
            "familiar": "Schedule one-time tasks. 'at now + 5 minutes', 'at 10:00 AM', atq to list, atrm to remove."
        },
        "nohup": {
            "beginner": "This runs a command that keeps going even after you close the terminal. The output gets saved to a file called 'nohup.out'.",
            "familiar": "Run command immune to hangups. Output to nohup.out. Often combined with & for background: nohup cmd &"
        },
        "bg": {
            "beginner": "This resumes a paused program and runs it in the background, so you can keep using your terminal while it works.",
            "familiar": "Resume suspended job in background. Use Ctrl+Z to suspend, bg to resume in background, fg to bring to foreground."
        },
        "fg": {
            "beginner": "This brings a background program back to the foreground of your terminal, so you can interact with it again.",
            "familiar": "Bring background job to foreground. fg %N for specific job number. Use 'jobs' to list background jobs."
        },
        "jobs": {
            "beginner": "This shows all the programs you have running or paused in the background of your current terminal session.",
            "familiar": "List background/suspended jobs. -l for PIDs. Use fg %N or bg %N to manage specific jobs."
        },
        "nice": {
            "beginner": "This starts a program with a specific priority level. Higher nice values mean lower priority (the program is being 'nice' by letting others go first).",
            "familiar": "Run command with adjusted scheduling priority. Range: -20 (highest) to 19 (lowest). Default is 0."
        },
        "renice": {
            "beginner": "This changes the priority of a program that's already running, making it use more or less CPU relative to other programs.",
            "familiar": "Alter priority of running process. renice -n priority -p PID. Root needed for negative (high priority) values."
        },
        "time": {
            "beginner": "This measures how long a command takes to run. It shows real time (wall clock), user time (CPU on your code), and system time (CPU on OS tasks).",
            "familiar": "Measure command execution time. Shows real (wall clock), user (CPU user-mode), and sys (CPU kernel-mode) time."
        },
        "timeout": {
            "beginner": "This runs a command but automatically stops it if it takes too long. For example, 'timeout 10 ping google.com' stops pinging after 10 seconds.",
            "familiar": "Run command with time limit. Sends SIGTERM at timeout, --signal to change. Duration supports s/m/h/d suffixes."
        },
        "yes": {
            "beginner": "This repeatedly outputs 'y' (or any text you specify). It's mainly used to automatically answer 'yes' to prompts from other commands.",
            "familiar": "Output a string repeatedly until killed. Commonly piped to commands that need confirmation: yes | apt install pkg"
        },
        "cal": {
            "beginner": "This displays a calendar in your terminal. By default it shows the current month. You can specify a month and year.",
            "familiar": "Display calendar. cal -3 for surrounding months, cal 2024 for full year, cal 6 2024 for specific month."
        },
        "bc": {
            "beginner": "This is a calculator you can use right in the terminal. Type math expressions and it gives you answers. Type 'quit' to exit.",
            "familiar": "Arbitrary precision calculator. -l for math library (enables decimals). Supports variables, functions, and programming constructs."
        },
        "tr": {
            "beginner": "This translates or deletes characters. For example, 'echo hello | tr a-z A-Z' converts text to uppercase.",
            "familiar": "Translate/delete characters. -d to delete, -s to squeeze repeats. Common: tr '[:lower:]' '[:upper:]' for case conversion."
        },
        "cut": {
            "beginner": "This extracts specific columns or parts of each line of text. For example, 'cut -d, -f1' gets the first column from a comma-separated file.",
            "familiar": "Extract sections of lines. -d for delimiter, -f for fields, -c for characters. Alternative: awk for complex extraction."
        },
        "paste": {
            "beginner": "This merges lines of files side by side. If you have two files with names and ages, paste combines them into one file with both.",
            "familiar": "Merge lines of files. -d for delimiter, -s for serial (one file per line). Opposite of cut."
        },
        "column": {
            "beginner": "This formats text into neat columns, making messy output look like a clean table.",
            "familiar": "Format output into columns. -t for table, -s for separator. Useful for formatting command output."
        },
        "rev": {
            "beginner": "This reverses each line of text. 'echo hello | rev' outputs 'olleh'. Occasionally useful for text manipulation.",
            "familiar": "Reverse lines character by character. Niche use cases in text processing pipelines."
        },
        "fold": {
            "beginner": "This wraps long lines of text to fit within a specified width. Useful for formatting text files.",
            "familiar": "Wrap lines to specified width. -w for width, -s to break at spaces instead of mid-word."
        },
        "fmt": {
            "beginner": "This reformats text to have a uniform line width, like adjusting margins in a word processor but for plain text files.",
            "familiar": "Simple text formatter. -w for width, -u for uniform spacing. Reformats paragraphs to specified width."
        },
        "split": {
            "beginner": "This splits a large file into smaller pieces. Useful when a file is too big to email or upload at once.",
            "familiar": "Split file into pieces. -l for lines, -b for bytes, -n for number of files. Use cat to reassemble."
        },
        "csplit": {
            "beginner": "This splits a file into pieces based on patterns or line numbers, giving you more control than 'split'.",
            "familiar": "Context-aware file splitting. Split based on regex patterns or line numbers. More flexible than split."
        },
        "comm": {
            "beginner": "This compares two sorted files line by line and shows which lines are unique to each file and which are common to both.",
            "familiar": "Compare sorted files. Three columns: unique to file1, unique to file2, common. -1 -2 -3 to suppress columns."
        },
        "join": {
            "beginner": "This combines two files based on a common field, like a database join. Both files must be sorted on the join field.",
            "familiar": "Join lines of two files on a common field. -t for delimiter, -1/-2 for join fields. Files must be sorted."
        },
        "patch": {
            "beginner": "This applies changes from a diff file to the original file. Used when someone sends you a set of changes to apply to code.",
            "familiar": "Apply diff/patch files. -p for strip path components. Reverse with -R. Common in open source development."
        },
        "basename": {
            "beginner": "This extracts just the filename from a full path. For example, 'basename /home/user/file.txt' gives you 'file.txt'.",
            "familiar": "Strip directory and suffix from filename. basename path [suffix]. Useful in shell scripts."
        },
        "dirname": {
            "beginner": "This extracts just the directory path from a full file path. For example, 'dirname /home/user/file.txt' gives you '/home/user'.",
            "familiar": "Strip last component from path. Returns directory portion. Useful in shell scripts for path manipulation."
        },
        "readlink": {
            "beginner": "This shows where a symbolic link (shortcut) actually points to, revealing the real file or folder behind the link.",
            "familiar": "Print resolved symbolic link. -f for full canonical path (resolves all symlinks). Useful for finding real paths."
        },
        "realpath": {
            "beginner": "This shows the full, absolute path to a file, resolving any shortcuts (symlinks) or relative references along the way.",
            "familiar": "Print resolved absolute path. Resolves symlinks and relative components. Useful in scripts for canonical paths."
        },
        "stat": {
            "beginner": "This shows detailed information about a file: its size, permissions, owner, when it was created, modified, and last accessed.",
            "familiar": "Display file/filesystem status. Shows inode, permissions, timestamps, size. -c for custom format."
        },
        "file": {
            "beginner": "This tells you what type a file is (text, image, executable, etc.) by looking at its contents, not just its name extension.",
            "familiar": "Determine file type by content analysis (magic bytes). -i for MIME type. Doesn't rely on file extension."
        },
        "locate": {
            "beginner": "This finds files on your computer very quickly by searching a database (much faster than 'find'). Run 'updatedb' first to refresh the database.",
            "familiar": "Find files by name using pre-built database. Run 'sudo updatedb' to refresh. -i for case-insensitive."
        },
        "updatedb": {
            "beginner": "This updates the database that 'locate' uses to find files quickly. Run it with sudo after adding new files if locate can't find them.",
            "familiar": "Update locate database. Usually runs via cron daily. sudo updatedb for manual refresh."
        },
        "whereis": {
            "beginner": "This finds where a program's executable, source code, and manual pages are located on your system.",
            "familiar": "Locate binary, source, and man pages. -b for binary only, -m for man only, -s for source only."
        },
        "type": {
            "beginner": "This tells you what kind of command something is \u2014 whether it's a built-in shell command, an alias, a function, or an external program.",
            "familiar": "Display command type (alias, builtin, function, file). -a to show all locations. Useful for debugging PATH issues."
        },
        "printenv": {
            "beginner": "This shows the value of environment variables. 'printenv PATH' shows your PATH, or use it without arguments to see all variables.",
            "familiar": "Print environment variables. Optionally specify variable name. Alternative: echo $VARNAME."
        },
        "set": {
            "beginner": "This shows or sets shell options and variables. Without arguments, it displays all shell variables and functions.",
            "familiar": "Set shell options/variables. -e to exit on error, -x for debug trace, -o pipefail for pipe error handling. Common in scripts."
        },
        "unset": {
            "beginner": "This removes an environment variable or shell function. After unsetting, the variable no longer exists in your session.",
            "familiar": "Remove shell variables or functions. unset VAR to remove variable, unset -f func to remove function."
        },
        "test": {
            "beginner": "This checks conditions in shell scripts, like whether a file exists or if two numbers are equal. Often written as [ condition ].",
            "familiar": "Evaluate conditional expressions. -f for file exists, -d for directory, -z for empty string, -eq for numeric equal. Same as [ ]."
        },
        "expr": {
            "beginner": "This evaluates simple math expressions and string operations in the shell. Most people now use $(( )) instead for math.",
            "familiar": "Evaluate expressions. Mostly replaced by $(( )) for arithmetic and [[ ]] for string operations in modern bash."
        },
        "seq": {
            "beginner": "This generates a sequence of numbers. 'seq 1 10' prints numbers 1 through 10, one per line. Useful in scripts for loops.",
            "familiar": "Print number sequences. seq START [STEP] END. -s for separator, -w for equal width padding."
        },
        "tput": {
            "beginner": "This controls terminal features like colors, cursor movement, and text formatting from scripts.",
            "familiar": "Terminal capability interface. cols/lines for dimensions, setaf/setab for colors, bold/sgr0 for formatting."
        },
        "docker run": {
            "beginner": "This starts a new container from a Docker image. Think of it as launching a mini-computer with a specific program pre-installed and ready to go.",
            "familiar": "Create and start container. -d for detached, -p for port mapping, -v for volume mount, --rm for auto-cleanup, -e for env vars."
        },
        "docker build": {
            "beginner": "This creates a Docker image from a Dockerfile (a recipe for building your container). It packages your app and all its dependencies.",
            "familiar": "Build image from Dockerfile. -t for tag, -f for Dockerfile path, --no-cache to rebuild from scratch, --build-arg for build variables."
        },
        "docker ps": {
            "beginner": "This shows all currently running Docker containers. Add '-a' to also see stopped containers.",
            "familiar": "List containers. -a for all (including stopped), -q for IDs only, --format for custom output."
        },
        "docker exec": {
            "beginner": "This runs a command inside a running container. 'docker exec -it container_name bash' opens a terminal inside the container.",
            "familiar": "Execute command in running container. -it for interactive terminal, -u for user, -w for working directory."
        },
        "docker logs": {
            "beginner": "This shows the output (logs) from a container. Useful for debugging when something isn't working inside a container.",
            "familiar": "Fetch container logs. -f to follow, --tail N for last N lines, --since for time filter."
        },
        "docker stop": {
            "beginner": "This gracefully stops a running container. The container can be started again later with 'docker start'.",
            "familiar": "Stop running container. Sends SIGTERM then SIGKILL after grace period. -t for custom timeout."
        },
        "docker rm": {
            "beginner": "This deletes a stopped container. Use 'docker rm -f' to force-remove a running container.",
            "familiar": "Remove container. -f to force (stops and removes), -v to remove associated volumes."
        },
        "docker images": {
            "beginner": "This lists all the Docker images stored on your computer. Images are the templates used to create containers.",
            "familiar": "List local images. -a for all (including intermediate), --format for custom output, -q for IDs only."
        },
        "docker rmi": {
            "beginner": "This deletes a Docker image from your computer. You need to remove any containers using it first.",
            "familiar": "Remove image. -f to force. Use docker image prune to remove dangling images."
        },
        "docker pull": {
            "beginner": "This downloads a Docker image from Docker Hub (an online library of pre-built images) to your computer.",
            "familiar": "Pull image from registry. Defaults to Docker Hub. Specify tag with image:tag, or --all-tags."
        },
        "docker push": {
            "beginner": "This uploads your Docker image to Docker Hub so others can download and use it.",
            "familiar": "Push image to registry. Login first with docker login. Tag with registry/image:tag for non-Docker Hub registries."
        },
        "docker-compose": {
            "beginner": "This manages multiple Docker containers together using a docker-compose.yml file. It starts, stops, and connects all the containers your app needs.",
            "familiar": "Multi-container orchestration. up -d to start, down to stop, logs to view, build to rebuild. Defined in docker-compose.yml."
        },
        "docker compose": {
            "beginner": "This is the modern version of docker-compose (built into Docker). It manages multiple containers defined in a docker-compose.yml file.",
            "familiar": "Docker Compose V2 (plugin). Same commands as docker-compose but as a Docker subcommand. up/down/logs/build/ps."
        },
        "docker volume": {
            "beginner": "This manages Docker volumes \u2014 persistent storage spaces that survive even when containers are deleted. Your data stays safe.",
            "familiar": "Manage volumes. create, ls, rm, inspect, prune. Volumes persist beyond container lifecycle."
        },
        "docker network": {
            "beginner": "This manages Docker networks that allow containers to communicate with each other, like creating a private network for your app's components.",
            "familiar": "Manage networks. create, ls, rm, inspect, connect/disconnect. Bridge is default, overlay for swarm."
        },
        "docker system prune": {
            "beginner": "This cleans up Docker by removing unused containers, images, networks, and build cache. Good for freeing up disk space.",
            "familiar": "Remove unused data. -a to remove all unused images, --volumes to include volumes. Reclaims disk space."
        },
        "kubectl": {
            "beginner": "This is the command-line tool for Kubernetes, a system that manages and runs containerized applications across multiple servers.",
            "familiar": "Kubernetes CLI. get/describe/apply/delete resources. -n for namespace, -o for output format (json/yaml/wide)."
        },
        "kubectl get": {
            "beginner": "This lists resources in your Kubernetes cluster. 'kubectl get pods' shows all running application instances, 'kubectl get services' shows network endpoints.",
            "familiar": "List resources. pods/services/deployments/nodes. -o wide for details, -o yaml for full spec, --all-namespaces."
        },
        "kubectl apply": {
            "beginner": "This creates or updates resources in Kubernetes using a YAML configuration file. It's the standard way to deploy applications.",
            "familiar": "Apply configuration. -f for file/directory, --dry-run=client for preview, -k for kustomize. Declarative management."
        },
        "kubectl describe": {
            "beginner": "This shows detailed information about a specific resource in Kubernetes, including events and conditions. Great for debugging.",
            "familiar": "Show detailed resource info including events, conditions, and status. kubectl describe pod/service/node NAME."
        },
        "kubectl logs": {
            "beginner": "This shows the output logs from an application running in Kubernetes. Useful for debugging when something isn't working.",
            "familiar": "Print container logs. -f to follow, --previous for crashed container, -c for specific container in multi-container pod."
        },
        "kubectl exec": {
            "beginner": "This runs a command inside a running Kubernetes pod. 'kubectl exec -it pod-name -- bash' opens a terminal inside the pod.",
            "familiar": "Execute command in pod. -it for interactive, -- before command. -c for specific container in multi-container pod."
        },
        "kubectl delete": {
            "beginner": "This removes resources from your Kubernetes cluster. 'kubectl delete pod my-pod' removes a specific pod.",
            "familiar": "Delete resources. -f for file-based, --all for all of type, --grace-period=0 for immediate. Cascading delete is default."
        },
        "kubectl scale": {
            "beginner": "This changes how many copies of your application are running. 'kubectl scale deployment my-app --replicas=3' runs 3 copies.",
            "familiar": "Scale deployment/replicaset replicas. kubectl scale deployment NAME --replicas=N. For auto-scaling, use HPA."
        },
        "helm": {
            "beginner": "Helm is a package manager for Kubernetes. It lets you install complex applications with a single command, like an app store for your cluster.",
            "familiar": "Kubernetes package manager. install/upgrade/rollback/uninstall charts. repo add for chart repositories."
        },
        "terraform": {
            "beginner": "Terraform lets you define your cloud infrastructure (servers, databases, networks) as code files, then creates or updates everything automatically.",
            "familiar": "Infrastructure as code. init/plan/apply/destroy. State management, modules, providers for cloud resources."
        },
        "terraform init": {
            "beginner": "This sets up Terraform for your project by downloading the necessary plugins (providers) for the cloud services you want to manage.",
            "familiar": "Initialize Terraform working directory. Downloads providers, initializes backend, prepares modules."
        },
        "terraform plan": {
            "beginner": "This shows you what changes Terraform will make to your infrastructure before actually making them. Always review the plan first.",
            "familiar": "Preview changes without applying. -out to save plan, -var for variables. Shows add/change/destroy counts."
        },
        "terraform apply": {
            "beginner": "This makes the actual changes to your cloud infrastructure based on your Terraform configuration files.",
            "familiar": "Apply infrastructure changes. -auto-approve to skip confirmation, -var for variables, -target for specific resources."
        },
        "terraform destroy": {
            "beginner": "This tears down all the infrastructure that Terraform created. Be very careful \u2014 this will delete real cloud resources.",
            "familiar": "Destroy all managed infrastructure. -target for specific resources, -auto-approve to skip confirmation."
        },
        "ansible": {
            "beginner": "Ansible automates tasks across many servers at once \u2014 installing software, configuring settings, deploying apps. All from one control machine.",
            "familiar": "IT automation tool. Uses YAML playbooks, agentless (SSH-based). ansible-playbook to run, -i for inventory."
        },
        "vagrant": {
            "beginner": "Vagrant creates and manages virtual machines for development. Define your dev environment in a file and share it with your team.",
            "familiar": "VM management for development. up/halt/destroy/ssh. Uses Vagrantfile for configuration. Supports VirtualBox, VMware, etc."
        },
        "aws": {
            "beginner": "This is the AWS command-line tool for managing Amazon cloud services like servers (EC2), storage (S3), and databases directly from your terminal.",
            "familiar": "AWS CLI. aws configure for setup, s3 for storage, ec2 for compute, iam for permissions. Use --profile for multiple accounts."
        },
        "aws s3": {
            "beginner": "This manages files in Amazon S3 (cloud storage). 'aws s3 cp file.txt s3://bucket/' uploads a file, 'aws s3 ls' lists your storage buckets.",
            "familiar": "S3 operations. cp/mv/rm/sync/ls/mb/rb. --recursive for directories, sync for efficient updates."
        },
        "aws ec2": {
            "beginner": "This manages virtual servers (instances) in Amazon's cloud. You can start, stop, and configure servers from the command line.",
            "familiar": "EC2 management. describe-instances, run-instances, start/stop/terminate-instances. Use --filters for queries."
        },
        "gcloud": {
            "beginner": "This is the Google Cloud command-line tool for managing Google Cloud services like servers, storage, and Kubernetes clusters.",
            "familiar": "Google Cloud CLI. gcloud init for setup, compute for VMs, container for GKE, config set for defaults."
        },
        "az": {
            "beginner": "This is the Azure command-line tool for managing Microsoft Azure cloud services like virtual machines, databases, and web apps.",
            "familiar": "Azure CLI. az login for auth, vm/webapp/sql/storage subcommands. az group for resource groups."
        },
        "git merge": {
            "beginner": "This combines changes from one branch into another. It's like taking work from a side project and adding it to your main project.",
            "familiar": "Merge branches. --no-ff for merge commit, --squash to combine commits, --abort to cancel conflicted merge."
        },
        "git rebase": {
            "beginner": "This moves your branch's changes on top of the latest main branch changes, creating a cleaner history. More advanced than merge.",
            "familiar": "Reapply commits on top of another base. -i for interactive (squash/reorder/edit commits), --abort to cancel."
        },
        "git stash": {
            "beginner": "This temporarily saves your uncommitted changes and gives you a clean working directory. Use 'git stash pop' to get them back later.",
            "familiar": "Temporarily shelve changes. pop to restore, list to show stashes, drop to discard, apply to restore without removing."
        },
        "git reset": {
            "beginner": "This undoes commits or unstages files. 'git reset HEAD file' unstages a file. 'git reset --hard' discards all changes (dangerous!).",
            "familiar": "Reset HEAD to a state. --soft keeps changes staged, --mixed unstages, --hard discards all. Dangerous for shared branches."
        },
        "git cherry-pick": {
            "beginner": "This takes a specific commit from another branch and applies it to your current branch. Like picking one specific change without merging everything.",
            "familiar": "Apply specific commits to current branch. -x to record source hash, --no-commit to stage without committing."
        },
        "git tag": {
            "beginner": "This marks a specific point in your project's history with a name, usually for releases like 'v1.0'. Tags are permanent bookmarks.",
            "familiar": "Create/list/delete tags. -a for annotated (recommended), -m for message, -d to delete. Push tags: git push --tags."
        },
        "git remote": {
            "beginner": "This manages connections to remote repositories (like GitHub). 'git remote -v' shows where your code is being pushed to.",
            "familiar": "Manage remote repositories. -v for verbose, add/remove/rename/set-url. origin is the default remote name."
        },
        "git fetch": {
            "beginner": "This downloads the latest changes from the remote repository but doesn't merge them. It lets you review changes before integrating them.",
            "familiar": "Download remote refs/objects without merging. --all for all remotes, --prune to remove deleted remote branches."
        },
        "git blame": {
            "beginner": "This shows who last changed each line of a file and when. Useful for finding out who wrote specific code (not for blaming people!).",
            "familiar": "Show line-by-line authorship. -L for line range, -w to ignore whitespace, -C to detect moved/copied lines."
        },
        "git bisect": {
            "beginner": "This helps you find which commit introduced a bug by automatically testing commits between a known good and bad version.",
            "familiar": "Binary search for buggy commit. start, good, bad to mark commits. Automate with: git bisect run test_script."
        },
        "git reflog": {
            "beginner": "This shows a log of everywhere your HEAD has pointed, including changes that git log won't show. A lifesaver for recovering lost commits.",
            "familiar": "Show reference log for HEAD. Useful for recovering from reset/rebase mistakes. Entries expire after 90 days."
        },
        "git submodule": {
            "beginner": "This lets you include other Git repositories inside your project. Like having a library project embedded within your main project.",
            "familiar": "Manage nested repositories. add/init/update/status. --recursive for nested submodules. Use subtree as simpler alternative."
        },
        "git worktree": {
            "beginner": "This lets you check out multiple branches at the same time in different directories, so you can work on two features simultaneously.",
            "familiar": "Manage multiple working trees. add/list/remove. Work on multiple branches without stashing. Linked to same .git."
        },
        "git switch": {
            "beginner": "This switches between branches. It's the newer, simpler replacement for 'git checkout' when you just want to change branches.",
            "familiar": "Switch branches. -c to create and switch, --detach for detached HEAD. Preferred over git checkout for branch switching."
        },
        "git restore": {
            "beginner": "This restores files to a previous state. It can undo changes to files in your working directory or unstage files.",
            "familiar": "Restore working tree files. --staged to unstage, --source to specify commit. Preferred over git checkout for file restoration."
        },
        "pip freeze": {
            "beginner": "This shows all installed Python packages and their versions. Often used to create a requirements.txt file for sharing your project's dependencies.",
            "familiar": "Output installed packages in requirements format. pip freeze > requirements.txt to save. --local for virtualenv only."
        },
        "pip uninstall": {
            "beginner": "This removes a Python package from your system. 'pip uninstall requests' removes the requests library.",
            "familiar": "Remove Python packages. -y to skip confirmation, -r to uninstall from requirements file."
        },
        "pip list": {
            "beginner": "This shows all Python packages currently installed, along with their version numbers.",
            "familiar": "List installed packages. --outdated for upgradable packages, --format for output format (columns/json/freeze)."
        },
        "pip show": {
            "beginner": "This displays detailed information about a specific installed Python package, including its version, dependencies, and location.",
            "familiar": "Show package details. Displays version, location, dependencies, required-by. Useful for dependency debugging."
        },
        "python -m venv": {
            "beginner": "This creates a virtual environment \u2014 an isolated space for your Python project's packages. It keeps your project's dependencies separate from other projects.",
            "familiar": "Create virtual environment. python -m venv env_name, then source env_name/bin/activate. Isolates project dependencies."
        },
        "python -m pip": {
            "beginner": "This runs pip through Python's module system, ensuring you use the right pip for your Python version. Same as 'pip' but more reliable.",
            "familiar": "Run pip via Python module. Ensures correct pip for the Python interpreter. Avoids PATH issues with multiple Python versions."
        },
        "python -m pytest": {
            "beginner": "This runs your Python tests using pytest, a popular testing framework. It automatically finds and runs test files in your project.",
            "familiar": "Run pytest test suite. -v for verbose, -x to stop on first failure, -k for keyword filter, --cov for coverage."
        },
        "python -m http.server": {
            "beginner": "This starts a simple web server that serves files from the current directory. Open your browser to localhost:8000 to see them.",
            "familiar": "Start simple HTTP server. Specify port: python -m http.server 3000. --bind for address. Not for production use."
        },
        "flask run": {
            "beginner": "This starts a Flask web application development server. Set FLASK_APP first to tell it which file to run.",
            "familiar": "Run Flask dev server. --host 0.0.0.0 for external access, --port for port, --debug for auto-reload. Not for production."
        },
        "uvicorn": {
            "beginner": "This runs a Python web application built with FastAPI or other ASGI frameworks. It's a fast, production-ready web server.",
            "familiar": "ASGI server. uvicorn app:app --reload for dev, --workers N for production, --host/--port for binding."
        },
        "gunicorn": {
            "beginner": "This is a production web server for Python applications. It runs multiple copies of your app to handle many users at once.",
            "familiar": "Production WSGI server. -w for workers (2*CPU+1), -b for bind address, -k for worker class (gevent/uvicorn)."
        },
        "celery": {
            "beginner": "Celery runs tasks in the background so your web app doesn't freeze while doing slow operations like sending emails or processing files.",
            "familiar": "Distributed task queue. celery -A app worker for workers, beat for scheduling. Requires broker (Redis/RabbitMQ)."
        },
        "django-admin": {
            "beginner": "This is the command-line tool for Django web projects. It helps you create projects, run the server, manage the database, and more.",
            "familiar": "Django management utility. startproject/startapp, runserver, migrate, makemigrations, createsuperuser, shell."
        },
        "manage.py": {
            "beginner": "This is your Django project's management script. 'python manage.py runserver' starts the development server, 'python manage.py migrate' sets up the database.",
            "familiar": "Django project management. runserver, migrate, makemigrations, createsuperuser, collectstatic, test, shell."
        },
        "pytest": {
            "beginner": "This runs your Python tests. It automatically finds files starting with 'test_' and runs functions starting with 'test_'. Green means pass, red means fail.",
            "familiar": "Python testing framework. -v for verbose, -x stop on first fail, -k for keyword filter, --cov for coverage, -s for print output."
        },
        "mypy": {
            "beginner": "This checks your Python code for type errors without running it. It catches bugs where you accidentally pass the wrong type of data to functions.",
            "familiar": "Static type checker. --strict for maximum checking, --ignore-missing-imports, --show-error-codes. Uses type annotations."
        },
        "black": {
            "beginner": "This automatically formats your Python code to follow a consistent style. It makes your code look clean and professional without you having to think about formatting.",
            "familiar": "Opinionated Python code formatter. --check for dry run, --diff to preview changes, -l for line length."
        },
        "ruff": {
            "beginner": "This is an extremely fast Python code checker that finds common mistakes, style issues, and potential bugs in your code.",
            "familiar": "Fast Python linter/formatter. ruff check for linting, ruff format for formatting. Replaces flake8/isort/black. Configurable via pyproject.toml."
        },
        "isort": {
            "beginner": "This automatically sorts and organizes the import statements at the top of your Python files.",
            "familiar": "Sort Python imports. --check for dry run, --diff for preview, --profile black for Black compatibility."
        },
        "flake8": {
            "beginner": "This checks your Python code for style issues and common mistakes, following the PEP 8 style guide.",
            "familiar": "Python linting tool. --max-line-length, --ignore for skip codes, --select for specific codes. Configurable via .flake8 or setup.cfg."
        },
        "pylint": {
            "beginner": "This analyzes your Python code for errors, coding standards, and design issues. It gives your code a quality score out of 10.",
            "familiar": "Python static analysis. --disable for skip checks, --generate-rcfile for config. More opinionated than flake8."
        },
        "poetry": {
            "beginner": "Poetry manages your Python project's dependencies and packaging. It's a modern alternative to pip that handles everything in one tool.",
            "familiar": "Python dependency management. init/add/install/update/build/publish. Uses pyproject.toml. Manages virtual environments."
        },
        "pdm": {
            "beginner": "PDM is a modern Python package manager that follows PEP standards. It manages dependencies without needing virtual environments.",
            "familiar": "PEP-compliant package manager. add/install/update/remove. Uses pyproject.toml and pdm.lock. PEP 582 local packages support."
        },
        "uv": {
            "beginner": "uv is an extremely fast Python package installer and virtual environment manager. It's a drop-in replacement for pip and venv, but much faster.",
            "familiar": "Ultra-fast Python package manager. uv pip install/uv venv for pip/venv replacements. Written in Rust, 10-100x faster than pip."
        },
        "conda": {
            "beginner": "Conda manages Python packages and environments, especially for data science. It can install non-Python dependencies that pip can't handle.",
            "familiar": "Package/environment manager. create/activate/install/update. Handles non-Python deps. Channels: conda-forge, defaults."
        },
        "jupyter": {
            "beginner": "This starts Jupyter Notebook, an interactive environment where you can write and run Python code in small blocks, with rich output like charts and tables.",
            "familiar": "Interactive notebooks. jupyter notebook/lab for web interface, nbconvert for export. Supports Python, R, Julia kernels."
        },
        "npx": {
            "beginner": "This runs Node.js packages without installing them permanently. 'npx create-react-app my-app' runs the React app creator without cluttering your system.",
            "familiar": "Execute npm packages. Runs locally installed or downloads temporarily. Great for one-off commands and project scaffolding."
        },
        "npm run": {
            "beginner": "This runs scripts defined in your package.json file. 'npm run dev' typically starts the development server, 'npm run build' creates a production build.",
            "familiar": "Execute package.json scripts. Common: dev, build, test, start, lint. -- to pass args to underlying command."
        },
        "npm init": {
            "beginner": "This creates a new package.json file for your Node.js project by asking you some questions. Use 'npm init -y' to skip the questions.",
            "familiar": "Initialize package.json. -y for defaults, npm init @scope for scoped initializer. Creates project configuration."
        },
        "npm update": {
            "beginner": "This updates all your project's Node.js packages to the latest versions allowed by your package.json version ranges.",
            "familiar": "Update packages to latest matching version range. --save to update package.json. npm outdated to check first."
        },
        "npm audit": {
            "beginner": "This checks your project's dependencies for known security vulnerabilities and suggests fixes.",
            "familiar": "Check for vulnerabilities. --fix to auto-fix, --audit-level for threshold. Reviews dependency tree for CVEs."
        },
        "npm publish": {
            "beginner": "This uploads your package to the npm registry so other developers can install and use it with 'npm install'.",
            "familiar": "Publish package to registry. --access public for scoped packages, --tag for version tag, --dry-run for preview."
        },
        "yarn": {
            "beginner": "Yarn is an alternative to npm for managing Node.js packages. It works the same way but some teams prefer it for its speed and features.",
            "familiar": "Alternative Node.js package manager. add/remove/upgrade/install. yarn.lock for deterministic installs. V1 (Classic) vs V2+ (Berry)."
        },
        "pnpm": {
            "beginner": "pnpm is a fast, disk-space efficient Node.js package manager. It shares packages between projects to save disk space.",
            "familiar": "Efficient package manager. Content-addressable storage, strict node_modules. add/install/update. Saves disk space vs npm/yarn."
        },
        "bun": {
            "beginner": "Bun is an all-in-one JavaScript runtime that's much faster than Node.js. It includes a package manager, bundler, and test runner.",
            "familiar": "Fast JS runtime/toolkit. bun install/run/test/build. Drop-in Node.js replacement. Built-in bundler and test runner."
        },
        "deno": {
            "beginner": "Deno is a modern JavaScript and TypeScript runtime created by the creator of Node.js. It has built-in TypeScript support and better security.",
            "familiar": "Secure JS/TS runtime. Built-in TypeScript, linter, formatter, test runner. Permissions model: --allow-net, --allow-read, etc."
        },
        "tsc": {
            "beginner": "This is the TypeScript compiler that converts TypeScript code into JavaScript. It checks for type errors and produces browser-ready code.",
            "familiar": "TypeScript compiler. --init for tsconfig.json, --watch for auto-recompile, --noEmit for type-checking only."
        },
        "eslint": {
            "beginner": "This checks your JavaScript/TypeScript code for errors and style issues, helping you write better, more consistent code.",
            "familiar": "JavaScript linter. --fix for auto-fix, --ext for file extensions. Config in .eslintrc or eslint.config.js (flat config)."
        },
        "prettier": {
            "beginner": "This automatically formats your JavaScript, HTML, CSS, and other files to look clean and consistent.",
            "familiar": "Opinionated code formatter. --check for dry run, --write to apply. Supports JS/TS/HTML/CSS/JSON/YAML/MD."
        },
        "vite": {
            "beginner": "Vite is a fast build tool for modern web applications. It starts a development server with instant hot reloading when you change your code.",
            "familiar": "Fast frontend build tool. vite/vite build/vite preview. HMR, ESM-based dev server. Config in vite.config.ts."
        },
        "webpack": {
            "beginner": "Webpack bundles all your web project's files (JavaScript, CSS, images) into optimized files for the browser.",
            "familiar": "Module bundler. webpack/webpack serve for dev. Config in webpack.config.js. Loaders for file types, plugins for optimization."
        },
        "next": {
            "beginner": "Next.js is a React framework for building websites. 'next dev' starts development, 'next build' creates a production build.",
            "familiar": "React framework. dev/build/start. App Router (app/) or Pages Router (pages/). SSR, SSG, ISR, API routes."
        },
        "create-react-app": {
            "beginner": "This scaffolds a new React project with everything set up and ready to go. Just run 'npx create-react-app my-app'.",
            "familiar": "React project scaffolding. Deprecated in favor of Next.js, Vite, or Remix. --template for variants."
        },
        "vue": {
            "beginner": "Vue CLI creates and manages Vue.js web application projects. 'npm create vue@latest' is the modern way to start a Vue project.",
            "familiar": "Vue.js CLI/tooling. vue create for CLI, npm create vue@latest for create-vue (Vite-based). serve/build/lint."
        },
        "ng": {
            "beginner": "This is the Angular CLI for creating and managing Angular web applications. 'ng new my-app' creates a new project, 'ng serve' starts the dev server.",
            "familiar": "Angular CLI. new/serve/build/generate/test. ng g component/service/module for scaffolding."
        },
        "svelte": {
            "beginner": "SvelteKit is a framework for building fast web applications. Create a project with 'npx sv create' and run with 'npm run dev'.",
            "familiar": "Svelte/SvelteKit. npm create svelte@latest for new project. Compiles away framework overhead at build time."
        },
        "astro": {
            "beginner": "Astro builds fast websites by shipping zero JavaScript by default. Great for content-heavy sites like blogs and documentation.",
            "familiar": "Content-focused web framework. npm create astro@latest. Islands architecture, partial hydration. Multi-framework support."
        },
        "go": {
            "beginner": "This runs Go programs. 'go run main.go' runs a file, 'go build' compiles it, 'go mod init' starts a new project.",
            "familiar": "Go toolchain. run/build/test/mod/get/fmt/vet. go mod init for modules, go mod tidy to sync dependencies."
        },
        "go build": {
            "beginner": "This compiles your Go code into an executable program that you can run directly without needing Go installed.",
            "familiar": "Compile Go packages. -o for output name, -ldflags for linker flags, GOOS/GOARCH for cross-compilation."
        },
        "go test": {
            "beginner": "This runs the tests in your Go project. Test files end with _test.go and test functions start with Test.",
            "familiar": "Run Go tests. -v for verbose, -run for filter, -bench for benchmarks, -cover for coverage, -race for race detection."
        },
        "go mod": {
            "beginner": "This manages your Go project's dependencies. 'go mod init' starts a new module, 'go mod tidy' cleans up unused dependencies.",
            "familiar": "Go module management. init/tidy/download/verify/vendor. go.mod defines module, go.sum for checksums."
        },
        "go fmt": {
            "beginner": "This automatically formats your Go code to follow the standard Go style. All Go code should be formatted this way.",
            "familiar": "Format Go source code. Standard formatting, no configuration. gofmt -s for simplification. Usually run via editor."
        },
        "cargo": {
            "beginner": "Cargo is Rust's package manager and build system. 'cargo new' creates a project, 'cargo build' compiles it, 'cargo run' builds and runs it.",
            "familiar": "Rust build system/package manager. new/build/run/test/check/clippy/fmt/publish. Config in Cargo.toml."
        },
        "cargo build": {
            "beginner": "This compiles your Rust project. Add '--release' for an optimized production build (slower to compile but faster to run).",
            "familiar": "Compile Rust project. --release for optimized build, --target for cross-compilation. Output in target/debug or target/release."
        },
        "cargo run": {
            "beginner": "This compiles and immediately runs your Rust program. It's the quickest way to test your code during development.",
            "familiar": "Build and run. --release for optimized, -- args for program arguments, -p for specific package in workspace."
        },
        "cargo test": {
            "beginner": "This runs all the tests in your Rust project. Tests are functions marked with #[test] attribute.",
            "familiar": "Run tests. -- --nocapture for stdout, --test-threads=1 for serial, --ignored for ignored tests. Doc tests run too."
        },
        "rustc": {
            "beginner": "This is the Rust compiler. It turns Rust code into executable programs. Most people use 'cargo' instead of calling rustc directly.",
            "familiar": "Rust compiler. Usually invoked through cargo. --edition for Rust edition, -O for optimization, --explain for error details."
        },
        "rustup": {
            "beginner": "This manages your Rust installation. It lets you install, update, and switch between different versions of the Rust compiler.",
            "familiar": "Rust toolchain installer. update/default/target/component. Manages stable/beta/nightly toolchains."
        },
        "javac": {
            "beginner": "This compiles Java source code (.java files) into bytecode (.class files) that the Java Virtual Machine can run.",
            "familiar": "Java compiler. -d for output directory, -cp for classpath, -source/-target for version compatibility."
        },
        "java": {
            "beginner": "This runs Java programs. You need to compile with 'javac' first, then run with 'java ClassName' (without the .class extension).",
            "familiar": "Run Java programs. -jar for JAR files, -cp for classpath, -Xmx for max heap, -D for system properties."
        },
        "jar": {
            "beginner": "This creates or extracts Java archive (JAR) files, which package Java applications and libraries into a single file.",
            "familiar": "Java archive tool. -cf to create, -xf to extract, -tf to list. -e for entry point in executable JARs."
        },
        "mvn": {
            "beginner": "Maven is a build tool for Java projects. 'mvn clean install' compiles your project, runs tests, and packages it.",
            "familiar": "Java build/dependency management. clean/compile/test/package/install/deploy. Config in pom.xml. -DskipTests to skip tests."
        },
        "gradle": {
            "beginner": "Gradle is a modern build tool for Java, Kotlin, and Android projects. 'gradle build' compiles and tests your project.",
            "familiar": "Build automation tool. build/test/clean/run. Groovy or Kotlin DSL in build.gradle. ./gradlew for wrapper (preferred)."
        },
        "ruby": {
            "beginner": "This runs Ruby programs. 'ruby script.rb' executes a Ruby file, or run 'irb' for an interactive Ruby console.",
            "familiar": "Run Ruby scripts. -e for inline code, -c for syntax check, -w for warnings. irb for interactive console."
        },
        "gem": {
            "beginner": "This is Ruby's package manager. 'gem install rails' installs the Rails framework. Gems are reusable libraries of Ruby code.",
            "familiar": "Ruby package manager. install/uninstall/list/search/update. --user-install for local gems. Gemfile with bundler preferred."
        },
        "bundle": {
            "beginner": "Bundler manages your Ruby project's dependencies listed in a Gemfile. 'bundle install' installs all required gems.",
            "familiar": "Ruby dependency manager. install/update/exec/lock. Uses Gemfile and Gemfile.lock. bundle exec to run in context."
        },
        "rails": {
            "beginner": "Ruby on Rails is a web application framework. 'rails new app' creates a project, 'rails server' starts it, 'rails generate' creates code.",
            "familiar": "Rails CLI. new/server/generate/console/db:migrate/routes. g model/controller/scaffold for code generation."
        },
        "rake": {
            "beginner": "Rake runs tasks defined in Ruby, similar to Makefiles. Rails uses it for database migrations, tests, and other maintenance tasks.",
            "familiar": "Ruby task runner. -T to list tasks, rake db:migrate for Rails migrations. Defined in Rakefile."
        },
        "make": {
            "beginner": "This runs build instructions from a Makefile. It's a classic tool for compiling programs. Just type 'make' to build your project.",
            "familiar": "Build automation from Makefile. make target to run specific target, -j for parallel, -f for alternate Makefile."
        },
        "cmake": {
            "beginner": "CMake generates build files for C/C++ projects. It creates the Makefiles that 'make' uses to compile your code.",
            "familiar": "Cross-platform build generator. mkdir build && cd build && cmake .. && make. -D for options, -G for generator."
        },
        "gcc": {
            "beginner": "This is the C/C++ compiler. It turns your C code into a program you can run. 'gcc hello.c -o hello' compiles hello.c into a program called hello.",
            "familiar": "GNU C/C++ compiler. -o output, -Wall for warnings, -g for debug symbols, -O2 for optimization, -l for libraries."
        },
        "g++": {
            "beginner": "This compiles C++ code into executable programs. It's the C++ version of gcc.",
            "familiar": "GNU C++ compiler. Same flags as gcc plus -std=c++17/c++20 for standard version. Links C++ standard library."
        },
        "clang": {
            "beginner": "Clang is a modern C/C++ compiler with better error messages than gcc. It works the same way but gives clearer explanations when something is wrong.",
            "familiar": "LLVM C/C++ compiler. Drop-in gcc replacement. Better diagnostics and error messages. Same flags as gcc."
        },
        "gdb": {
            "beginner": "This is a debugger for C/C++ programs. It lets you pause your program, step through it line by line, and inspect variables to find bugs.",
            "familiar": "GNU debugger. break/run/next/step/continue/print/backtrace. Compile with -g for symbols. Use tui mode for visual."
        },
        "valgrind": {
            "beginner": "This checks your C/C++ programs for memory problems like leaks (memory you forgot to free). It runs your program in a special way to detect issues.",
            "familiar": "Memory debugging/profiling. --leak-check=full for detailed leak info, --track-origins=yes for uninitialized values."
        },
        "ldconfig": {
            "beginner": "This updates the system's shared library cache so programs can find the libraries they need to run.",
            "familiar": "Configure dynamic linker cache. -p to print cache, add paths to /etc/ld.so.conf.d/. Run after installing libraries."
        },
        "ldd": {
            "beginner": "This shows which shared libraries (dependencies) a program needs to run. Useful for debugging 'library not found' errors.",
            "familiar": "Print shared library dependencies. Shows which .so files are needed and resolved paths. Don't use on untrusted binaries."
        },
        "objdump": {
            "beginner": "This displays information about compiled programs, like their machine code instructions. Mostly used by advanced developers.",
            "familiar": "Display object file info. -d for disassembly, -h for headers, -t for symbols, -S for source interleaved."
        },
        "nm": {
            "beginner": "This lists the symbols (function and variable names) in a compiled program or library. Used for debugging linking issues.",
            "familiar": "List symbols from object files. -D for dynamic symbols, -C for demangled C++ names, -u for undefined symbols."
        },
        "strip": {
            "beginner": "This removes debugging information from compiled programs to make them smaller. The program still works but can't be debugged as easily.",
            "familiar": "Remove symbols from object files. Reduces binary size. Use before distribution. --strip-debug for debug info only."
        },
        "mysql": {
            "beginner": "This opens a connection to a MySQL database where you can run SQL commands to create, read, update, and delete data.",
            "familiar": "MySQL client. -u for user, -p for password prompt, -h for host, -e for execute query. Use \\G for vertical output."
        },
        "psql": {
            "beginner": "This opens a connection to a PostgreSQL database where you can run SQL commands. Use \\q to quit, \\dt to list tables, \\? for help.",
            "familiar": "PostgreSQL client. -U for user, -d for database, -h for host, -c for execute. \\dt tables, \\d+ table for schema."
        },
        "sqlite3": {
            "beginner": "This opens a SQLite database file and lets you run SQL queries. SQLite is a lightweight database stored in a single file.",
            "familiar": "SQLite CLI. .tables to list, .schema for DDL, .mode for output format, .import for CSV. Database is a single file."
        },
        "mongo": {
            "beginner": "This connects to a MongoDB database where data is stored as flexible documents (like JSON) instead of rigid tables.",
            "familiar": "MongoDB shell (legacy). mongosh is the modern replacement. db.collection.find(), insertOne(), updateOne(), deleteOne()."
        },
        "mongosh": {
            "beginner": "This is the modern MongoDB shell for interacting with MongoDB databases. You can query, insert, and manage your data.",
            "familiar": "Modern MongoDB shell. db.collection.find/insertOne/updateOne/deleteOne. show dbs/collections. Supports JavaScript."
        },
        "redis-cli": {
            "beginner": "This connects to a Redis database, a fast in-memory data store often used for caching and real-time applications.",
            "familiar": "Redis command-line client. GET/SET/DEL/KEYS/HSET/LPUSH. INFO for stats, MONITOR for real-time commands, --pipe for bulk."
        },
        "pg_dump": {
            "beginner": "This creates a backup of a PostgreSQL database. You can save it as a file and restore it later if something goes wrong.",
            "familiar": "PostgreSQL backup. -F c for custom format, -F p for plain SQL, -t for specific table, --data-only/--schema-only."
        },
        "pg_restore": {
            "beginner": "This restores a PostgreSQL database from a backup file created by pg_dump.",
            "familiar": "Restore PostgreSQL backup. -d for target database, -j for parallel, --clean to drop before restore, -t for specific table."
        },
        "mysqldump": {
            "beginner": "This creates a backup of a MySQL database. It outputs SQL commands that can recreate the entire database.",
            "familiar": "MySQL backup utility. --single-transaction for InnoDB, --routines for stored procedures, --all-databases for full backup."
        },
        "jq": {
            "beginner": "This is a tool for working with JSON data. It can format, filter, and transform JSON from the command line. Very useful with APIs.",
            "familiar": "JSON processor. . for pretty-print, .key for field, .[] for array, select() for filtering, -r for raw output."
        },
        "yq": {
            "beginner": "This works with YAML files the same way jq works with JSON. Useful for reading and modifying configuration files.",
            "familiar": "YAML processor (like jq for YAML). Read/write/merge YAML files. Supports JSON and XML too. Multiple implementations exist."
        },
        "jid": {
            "beginner": "This is an interactive JSON explorer. Paste JSON data and interactively drill down into its structure.",
            "familiar": "Interactive JSON drill-down tool. Pipe JSON data to jid for interactive exploration."
        },
        "openssl": {
            "beginner": "This is a toolkit for working with encryption, SSL certificates, and secure connections. Used to create and manage security certificates.",
            "familiar": "Cryptography toolkit. req for CSR, x509 for certs, s_client for TLS testing, genrsa/genpkey for keys, enc for encryption."
        },
        "ssh-keygen": {
            "beginner": "This creates SSH keys \u2014 a pair of files used to securely identify you to remote servers without a password. Like a digital ID card.",
            "familiar": "Generate SSH key pairs. -t for algorithm (ed25519 recommended), -b for bits, -f for filename, -C for comment."
        },
        "ssh-copy-id": {
            "beginner": "This copies your SSH public key to a remote server so you can log in without typing your password every time.",
            "familiar": "Install SSH public key on remote server. Appends to ~/.ssh/authorized_keys. -i for specific key file."
        },
        "gpg": {
            "beginner": "This encrypts and signs files and messages. It uses public-key cryptography so you can securely share information.",
            "familiar": "GNU Privacy Guard. --gen-key to create keys, -e to encrypt, -d to decrypt, --sign to sign, --verify to verify."
        },
        "sha256sum": {
            "beginner": "This creates a unique fingerprint (checksum) of a file. You can use it to verify that a downloaded file hasn't been corrupted or tampered with.",
            "familiar": "Compute SHA-256 checksum. -c to verify against checksum file. Also: md5sum, sha1sum, sha512sum."
        },
        "md5sum": {
            "beginner": "This creates an MD5 checksum of a file \u2014 a short code that changes if the file is modified. Used to verify file integrity.",
            "familiar": "Compute MD5 hash. -c to verify. Note: MD5 is cryptographically broken, use SHA-256 for security purposes."
        },
        "base64": {
            "beginner": "This converts data to/from Base64 encoding. Base64 represents binary data as text, which is useful for embedding data in text formats.",
            "familiar": "Base64 encode/decode. -d to decode, -w 0 for no line wrapping. Common in APIs, email attachments, data URIs."
        },
        "xxd": {
            "beginner": "This shows the raw bytes of a file in hexadecimal format. It lets you see exactly what's in a file at the binary level.",
            "familiar": "Hex dump utility. -r for reverse (hex to binary), -p for plain hexdump, -l for length limit."
        },
        "strings": {
            "beginner": "This extracts readable text from binary files. Useful for finding error messages or other text hidden inside compiled programs.",
            "familiar": "Print printable strings from binary files. -n for minimum length. Useful for reverse engineering and binary analysis."
        },
        "iconv": {
            "beginner": "This converts text files between different character encodings (like UTF-8 and ASCII). Useful when text appears garbled.",
            "familiar": "Convert text encoding. -f for source encoding, -t for target, -l to list encodings. Common: UTF-8, ASCII, ISO-8859-1."
        },
        "od": {
            "beginner": "This displays file contents in octal (base-8) or other number formats. Used for examining binary file data.",
            "familiar": "Octal dump. -A for address format, -t for output format (x for hex, c for char, d for decimal)."
        },
        "hexdump": {
            "beginner": "This displays file contents in hexadecimal format. Like a more detailed view of what's actually stored in a file.",
            "familiar": "Display file in hex format. -C for canonical (hex + ASCII), -n for length limit, -s for skip offset."
        },
        "apt-get": {
            "beginner": "This is the older way to install software on Debian/Ubuntu Linux. 'apt-get install name' installs a package. Most people use 'apt' now instead.",
            "familiar": "Legacy Debian package manager. install/remove/update/upgrade/autoremove. Prefer apt for interactive use."
        },
        "dpkg": {
            "beginner": "This installs or manages individual .deb package files on Debian/Ubuntu Linux. It's lower-level than apt.",
            "familiar": "Debian package manager (low-level). -i to install, -r to remove, -l to list, -L to list files, -S to find package owning file."
        },
        "yum": {
            "beginner": "This installs software on Red Hat/CentOS Linux systems. 'yum install name' installs a package.",
            "familiar": "Legacy RHEL/CentOS package manager. install/remove/update/search. Replaced by dnf on modern systems."
        },
        "dnf": {
            "beginner": "This is the modern package manager for Fedora and Red Hat Linux. 'dnf install name' installs software.",
            "familiar": "Modern RHEL/Fedora package manager. install/remove/update/search/info. Replaces yum. Config in /etc/dnf/dnf.conf."
        },
        "pacman": {
            "beginner": "This is the package manager for Arch Linux. 'pacman -S name' installs a package, 'pacman -Syu' updates everything.",
            "familiar": "Arch Linux package manager. -S install, -R remove, -Syu full upgrade, -Ss search, -Q query installed."
        },
        "snap": {
            "beginner": "This installs software packaged as Snaps, which are self-contained and work across different Linux distributions.",
            "familiar": "Snap package manager. install/remove/refresh/list. Snaps are containerized, auto-updating packages."
        },
        "flatpak": {
            "beginner": "This installs apps from Flathub in a sandboxed environment. Apps are isolated from your system for better security.",
            "familiar": "Sandboxed application packaging. install/run/update/remove. Apps from Flathub. Runs in isolated environment."
        },
        "systemd-analyze": {
            "beginner": "This shows how long your system took to boot up and which services were slowest, helping you speed up startup time.",
            "familiar": "Analyze systemd boot performance. blame for per-unit timing, critical-chain for dependency chain, plot for SVG chart."
        },
        "hostnamectl": {
            "beginner": "This shows or changes your computer's hostname and other system identity information on systems using systemd.",
            "familiar": "Set system hostname. set-hostname for static, --transient/--pretty for other types. Shows OS info."
        },
        "timedatectl": {
            "beginner": "This shows or sets the system date, time, and timezone. 'timedatectl set-timezone America/New_York' changes your timezone.",
            "familiar": "Manage system time settings. set-time, set-timezone, set-ntp. list-timezones for available zones."
        },
        "localectl": {
            "beginner": "This shows or changes the system language, keyboard layout, and locale settings.",
            "familiar": "Manage system locale settings. set-locale, set-keymap. list-locales/list-keymaps for available options."
        },
        "ip addr": {
            "beginner": "This shows all the IP addresses assigned to your computer's network interfaces. It tells you your local network address.",
            "familiar": "Show/manage IP addresses. add/del for address management. Replaces ifconfig. ip addr show dev eth0 for specific interface."
        },
        "ip route": {
            "beginner": "This shows how your computer routes internet traffic \u2014 where it sends data to reach different networks.",
            "familiar": "Show/manage routing table. add/del for routes. Shows default gateway. ip route get IP to trace path."
        },
        "ip link": {
            "beginner": "This shows information about your network interfaces (Ethernet, Wi-Fi, etc.) and lets you enable/disable them.",
            "familiar": "Show/manage network interfaces. set dev up/down to enable/disable, show for listing. Replaces ifconfig."
        },
        "iwconfig": {
            "beginner": "This shows information about your wireless network connection and lets you configure Wi-Fi settings.",
            "familiar": "Wireless network configuration. Shows SSID, signal strength, bitrate. Deprecated in favor of iw."
        },
        "nmcli": {
            "beginner": "This manages network connections from the command line. You can connect to Wi-Fi, configure IP addresses, and manage VPNs.",
            "familiar": "NetworkManager CLI. con show for connections, dev status for devices, con up/down for manage. General networking management."
        },
        "arp": {
            "beginner": "This shows the mapping between IP addresses and hardware (MAC) addresses on your local network.",
            "familiar": "Show/manage ARP cache. -a to display, -d to delete entry. ip neigh is the modern replacement."
        },
        "route": {
            "beginner": "This shows or modifies the network routing table \u2014 the rules your computer uses to send network traffic to the right destination.",
            "familiar": "Show/manipulate routing table. Legacy command, use 'ip route' instead. -n for numeric output."
        },
        "ethtool": {
            "beginner": "This displays or changes Ethernet network adapter settings like speed, duplex mode, and Wake-on-LAN.",
            "familiar": "Query/control network driver settings. -i for driver info, -S for NIC stats, -s for speed/duplex."
        },
        "awk '{print $1}'": {
            "beginner": "This prints just the first column of text. Each space-separated word is a column. Very useful for extracting data from command output.",
            "familiar": "Print first field (space-delimited). Combine: awk -F',' '{print $2}' for CSV, awk 'NR>1' to skip header."
        },
        "xdg-open": {
            "beginner": "This opens a file or URL with the default application, just like double-clicking it in a file manager. Linux equivalent of macOS 'open'.",
            "familiar": "Open file/URL with default application. Linux desktop standard. macOS equivalent: open. Windows: start."
        },
        "open": {
            "beginner": "This opens a file, folder, or URL with the default application on macOS. Like double-clicking it in Finder.",
            "familiar": "macOS: open files/URLs/apps with default handler. -a for specific app, -R to reveal in Finder."
        },
        "pbcopy": {
            "beginner": "This copies text to the clipboard on macOS. For example, 'cat file.txt | pbcopy' copies the file's contents so you can paste them.",
            "familiar": "macOS: copy stdin to clipboard. Pair with pbpaste. Linux alternatives: xclip, xsel."
        },
        "pbpaste": {
            "beginner": "This outputs whatever is currently on your clipboard on macOS. Useful for pasting clipboard contents into files or commands.",
            "familiar": "macOS: paste clipboard contents to stdout. Pair with pbcopy. Linux alternatives: xclip -o, xsel -o."
        },
        "xclip": {
            "beginner": "This copies text to or from the clipboard on Linux. 'echo hello | xclip -selection clipboard' copies text for pasting.",
            "familiar": "Linux clipboard utility. -selection clipboard for system clipboard, -o to output. Alternative: xsel."
        },
        "cURL": {
            "beginner": "Another way to write 'curl' \u2014 this downloads data from URLs or sends data to web servers from your terminal.",
            "familiar": "See 'curl'. Case-insensitive command name on most systems."
        },
        "htpasswd": {
            "beginner": "This creates password files for web server authentication. Used to add password protection to websites served by Apache or Nginx.",
            "familiar": "Manage Apache/Nginx basic auth passwords. -c to create file, -B for bcrypt, -D to delete user."
        },
        "ab": {
            "beginner": "Apache Bench tests how many requests per second your web server can handle. It's a simple load testing tool.",
            "familiar": "Apache HTTP benchmarking. -n for requests, -c for concurrency, -H for headers. Simple load testing."
        },
        "wrk": {
            "beginner": "This is a modern HTTP benchmarking tool that tests how well your web server performs under heavy load.",
            "familiar": "HTTP benchmarking tool. -t threads, -c connections, -d duration, -s for Lua scripts. Better than ab."
        },
        "hey": {
            "beginner": "This sends a lot of requests to a web server to test how fast it responds. A simple way to load-test your application.",
            "familiar": "HTTP load testing. -n requests, -c concurrency, -z duration, -m method, -H headers. Go-based alternative to ab."
        },
        "envsubst": {
            "beginner": "This replaces placeholder variables in a file with their actual values from environment variables. Useful for configuration templates.",
            "familiar": "Substitute environment variables in text. Replaces $VAR or ${VAR} patterns. Useful for config templating."
        },
        "cmp": {
            "beginner": "This compares two files byte by byte and tells you the first position where they differ. Faster than diff for binary files.",
            "familiar": "Compare files byte by byte. -s for silent (exit code only), -l for all differences. Faster than diff for binary."
        },
        "wait": {
            "beginner": "This pauses your shell script until background processes finish running. It waits for all background jobs to complete.",
            "familiar": "Wait for background processes. wait PID for specific process, wait for all. Returns exit status of waited process."
        },
        "trap": {
            "beginner": "This catches signals (like Ctrl+C) in shell scripts and runs cleanup code before the script exits.",
            "familiar": "Handle signals in shell scripts. trap 'cleanup' EXIT/INT/TERM. Common for temp file cleanup and graceful shutdown."
        },
        "getopts": {
            "beginner": "This parses command-line options in shell scripts. It helps your script accept flags like -v or -f filename.",
            "familiar": "Parse shell script options. while getopts 'vf:' opt; do case $opt in... Options with : require arguments."
        },
        "read": {
            "beginner": "This reads input from the user in a shell script. The script pauses and waits for you to type something and press Enter.",
            "familiar": "Read user input. -p for prompt, -s for silent (passwords), -r for raw (no backslash escaping), -t for timeout."
        },
        "shellcheck": {
            "beginner": "This checks your shell scripts for common mistakes and gives you suggestions to fix them. Like a spell-checker for scripts.",
            "familiar": "Shell script linter. Catches common bash pitfalls, quoting issues, and portability problems. Available as CLI and editor plugin."
        },
        "shfmt": {
            "beginner": "This automatically formats your shell scripts to look clean and consistent.",
            "familiar": "Shell script formatter. -i for indent size, -ci for case indent, -bn for binary next-line. By mvdan."
        },
        "parallel": {
            "beginner": "GNU Parallel runs multiple commands at the same time, using all your CPU cores. It makes batch processing much faster.",
            "familiar": "Parallel command execution. Replaces xargs -P. -j for jobs, ::: for args, --pipe for piped input."
        },
        "expect": {
            "beginner": "This automates interactions with programs that expect keyboard input. It can type responses to prompts automatically.",
            "familiar": "Automate interactive programs. spawn/expect/send pattern. Useful for automating ssh, ftp, passwd, etc."
        },
        "socat": {
            "beginner": "Socat connects two data streams together. It's like a more powerful version of netcat that supports many different connection types.",
            "familiar": "Multipurpose relay (socket cat). Bidirectional data transfer between any two address types. TCP/UDP/Unix/files/exec."
        },
        "fzf": {
            "beginner": "This is a fuzzy finder that lets you search through lists of files, commands, or any text interactively. Type to filter results.",
            "familiar": "Fuzzy finder. Pipe any list to fzf for interactive selection. Integrates with shell (Ctrl+R for history, Alt+C for cd)."
        },
        "fd": {
            "beginner": "This is a simpler, faster alternative to 'find' for searching files. 'fd pattern' finds files matching the pattern.",
            "familiar": "User-friendly alternative to find. fd pattern for regex search, -e for extension, -t for type, -x for exec. Written in Rust."
        },
        "rg": {
            "beginner": "ripgrep is a super-fast search tool that finds text in files, much faster than grep. It respects .gitignore files automatically.",
            "familiar": "Fast grep alternative (ripgrep). -i case-insensitive, -l files only, -t type filter, --hidden for hidden files. Respects .gitignore."
        },
        "bat": {
            "beginner": "This is like 'cat' but with syntax highlighting, line numbers, and git integration. It makes viewing files much more pleasant.",
            "familiar": "cat clone with syntax highlighting. --language for forced highlighting, -A for non-printable chars, --diff for git changes."
        },
        "exa": {
            "beginner": "This is a modern replacement for 'ls' with colors, icons, and git status integration. Makes directory listings much prettier.",
            "familiar": "Modern ls replacement. -l for long, -a for all, --tree for tree view, --git for git status. Successor: eza."
        },
        "eza": {
            "beginner": "This is a modern, maintained replacement for 'ls' with colors, icons, and extra features. Successor to exa.",
            "familiar": "Modern ls replacement (successor to exa). -l/-a/--tree/--git/--icons. Actively maintained. Written in Rust."
        },
        "zoxide": {
            "beginner": "This is a smarter 'cd' that remembers directories you visit often. Type 'z project' to jump to your project folder from anywhere.",
            "familiar": "Smarter cd. Learns from your usage. z keyword for fuzzy jump, zi for interactive. Replaces cd for frequent dirs."
        },
        "tldr": {
            "beginner": "This shows simple, practical examples for commands. Much easier to read than man pages. 'tldr tar' shows common tar uses.",
            "familiar": "Simplified man pages with practical examples. Community-maintained. tldr command for quick reference."
        },
        "gh": {
            "beginner": "This is GitHub's official command-line tool. You can create repos, pull requests, issues, and more without opening a web browser.",
            "familiar": "GitHub CLI. repo/pr/issue/release/workflow subcommands. gh pr create, gh issue list, gh auth login."
        },
        "git init": {
            "beginner": "This creates a new Git repository in your current folder, enabling version control so you can track changes to your files.",
            "familiar": "Initialize new Git repository. Creates .git directory. --bare for bare repo. -b for initial branch name."
        },
        "git config": {
            "beginner": "This sets up your Git preferences, like your name and email that appear on your commits. Run 'git config --global user.name \"Your Name\"'.",
            "familiar": "Get/set Git configuration. --global for user-wide, --local for repo. user.name, user.email, core.editor common settings."
        },
        "git show": {
            "beginner": "This displays detailed information about a specific commit, including what files were changed and the actual changes made.",
            "familiar": "Show commit details with diff. git show HEAD for latest, git show hash:file for file at commit, --stat for summary."
        },
        "git clean": {
            "beginner": "This removes untracked files from your project. Use with caution \u2014 deleted files can't be recovered. Always use -n first to preview.",
            "familiar": "Remove untracked files. -f to force, -d for directories, -n for dry run, -x for ignored files too."
        },
        "git revert": {
            "beginner": "This safely undoes a commit by creating a new commit that reverses the changes. Unlike reset, it doesn't erase history.",
            "familiar": "Undo commit by creating inverse commit. Safer than reset for shared branches. -n for no auto-commit."
        },
        "git archive": {
            "beginner": "This creates a zip or tar file of your project at a specific commit, without including the .git folder.",
            "familiar": "Create archive of git tree. --format=zip/tar, --prefix for directory prefix. Excludes .git directory."
        },
        "git shortlog": {
            "beginner": "This shows a summary of commits grouped by author. Great for seeing who has contributed to the project.",
            "familiar": "Summarize commits by author. -s for count only, -n for sort by count, -e for email."
        },
        "git lfs": {
            "beginner": "Git Large File Storage handles big files (like images, videos, datasets) that don't work well with regular Git.",
            "familiar": "Large File Storage. git lfs track '*.psd' to track patterns, install to set up hooks. Stores files on LFS server."
        },
        "docker inspect": {
            "beginner": "This shows detailed information about a Docker container or image in JSON format, including its configuration and network settings.",
            "familiar": "Return low-level info on Docker objects. -f for format template. Works for containers, images, volumes, networks."
        },
        "docker cp": {
            "beginner": "This copies files between your computer and a Docker container. Like a copy command that crosses the container boundary.",
            "familiar": "Copy files between container and host. docker cp file container:/path or docker cp container:/path file."
        },
        "docker tag": {
            "beginner": "This gives a Docker image a new name or version tag, like labeling a box with a new label.",
            "familiar": "Create tag for image. docker tag source target:tag. Required before pushing to registries."
        },
        "docker commit": {
            "beginner": "This saves the current state of a container as a new image. Like taking a snapshot you can reuse later.",
            "familiar": "Create image from container. -m for message, -a for author. Prefer Dockerfiles for reproducible builds."
        },
        "docker save": {
            "beginner": "This saves a Docker image to a file so you can transfer it to another computer without using Docker Hub.",
            "familiar": "Export image to tar archive. docker save -o file.tar image. Load with docker load. For offline image transfer."
        },
        "docker load": {
            "beginner": "This imports a Docker image from a file that was created with 'docker save'. Used for offline image transfer.",
            "familiar": "Import image from tar archive. docker load -i file.tar. Complements docker save for offline transfer."
        },
        "docker stats": {
            "beginner": "This shows live resource usage (CPU, memory, network) for all running Docker containers, like a task manager for containers.",
            "familiar": "Live container resource usage. --no-stream for single snapshot, --format for custom output."
        },
        "docker top": {
            "beginner": "This shows the processes running inside a Docker container, similar to the 'ps' command but for containers.",
            "familiar": "Display running processes in container. Similar to ps but for container context."
        },
        "docker diff": {
            "beginner": "This shows what files have been added, modified, or deleted inside a container since it was started.",
            "familiar": "Show filesystem changes in container. A for added, C for changed, D for deleted."
        },
        "docker history": {
            "beginner": "This shows the layers and commands that were used to build a Docker image, like a recipe history.",
            "familiar": "Show image build history. --no-trunc for full commands. Shows each layer with size and creation command."
        },
        "docker login": {
            "beginner": "This logs you into Docker Hub or another container registry so you can push and pull private images.",
            "familiar": "Log into container registry. -u for username, -p for password (insecure, use --password-stdin). Default: Docker Hub."
        },
        "Dockerfile": {
            "beginner": "A Dockerfile is a recipe file that tells Docker how to build an image. It lists the base image, files to copy, and commands to run.",
            "familiar": "Container build instructions. FROM/RUN/COPY/CMD/EXPOSE/ENV/WORKDIR directives. Multi-stage builds for smaller images."
        },
        "pip3": {
            "beginner": "This is the package installer specifically for Python 3. Use it instead of 'pip' when your system has both Python 2 and Python 3.",
            "familiar": "Python 3 specific pip. Same commands as pip. Use when both Python 2 and 3 are installed."
        },
        "python3": {
            "beginner": "This runs Python 3 specifically. Use it when your system has both Python 2 and Python 3 to make sure you use the right version.",
            "familiar": "Python 3 interpreter. Use when both Python 2 and 3 are installed. python3 -m module for module execution."
        },
        "node --inspect": {
            "beginner": "This starts Node.js with the debugger enabled. You can connect Chrome DevTools or VS Code to step through your code.",
            "familiar": "Node.js debugging. --inspect for normal, --inspect-brk to break on start. Connect via chrome://inspect."
        },
        "npm ci": {
            "beginner": "This installs your project's exact dependencies from the lock file. Faster and more reliable than 'npm install' for CI/CD pipelines.",
            "familiar": "Clean install from package-lock.json. Removes node_modules first. Deterministic installs for CI/CD."
        },
        "npm link": {
            "beginner": "This creates a symbolic link to a local package, letting you test a package you're developing in another project without publishing it.",
            "familiar": "Symlink local package for development. npm link in package dir, then npm link pkg-name in consumer. Useful for local dev."
        },
        "npm cache": {
            "beginner": "This manages npm's download cache. 'npm cache clean --force' clears the cache, which can fix some installation problems.",
            "familiar": "Manage npm cache. clean --force to clear, verify to check integrity. Cache at ~/.npm."
        },
        "npx create-next-app": {
            "beginner": "This creates a new Next.js (React) web application with everything set up and ready to go.",
            "familiar": "Scaffold Next.js project. --typescript, --tailwind, --app for App Router, --src-dir for src directory."
        },
        "vercel": {
            "beginner": "This deploys your web application to Vercel's cloud platform. Just run 'vercel' in your project directory and it handles everything.",
            "familiar": "Vercel deployment CLI. vercel for preview, vercel --prod for production. Automatic framework detection. env/secrets management."
        },
        "netlify": {
            "beginner": "This deploys your web application to Netlify's hosting platform. 'netlify deploy' pushes your site live.",
            "familiar": "Netlify CLI. deploy for preview, deploy --prod for production. functions/dev for serverless. Sites and forms management."
        },
        "fly": {
            "beginner": "Fly.io CLI deploys applications close to users around the world. 'fly launch' sets up a new app, 'fly deploy' pushes updates.",
            "familiar": "Fly.io CLI. launch/deploy/status/logs/ssh. fly.toml for config. Global deployment with edge locations."
        },
        "heroku": {
            "beginner": "This deploys web applications to Heroku's cloud platform. 'heroku create' makes a new app, 'git push heroku main' deploys it.",
            "familiar": "Heroku CLI. create/apps/logs/config/run/ps. Deploy via git push. Buildpack-based. heroku run bash for shell."
        },
        "supervisord": {
            "beginner": "This manages and monitors multiple processes (programs) on your server. It can automatically restart programs if they crash.",
            "familiar": "Process control system. supervisorctl for management. Config in supervisord.conf. Ensures processes stay running."
        },
        "pm2": {
            "beginner": "PM2 keeps your Node.js applications running 24/7, automatically restarting them if they crash. 'pm2 start app.js' starts your app.",
            "familiar": "Node.js process manager. start/stop/restart/logs/monit. --watch for auto-restart on changes, cluster mode for scaling."
        },
        "nginx": {
            "beginner": "Nginx is a web server that serves websites and acts as a reverse proxy. It's one of the most popular web servers in the world.",
            "familiar": "Web server/reverse proxy. -t for config test, -s reload/stop/reopen. Config in /etc/nginx/. Sites in sites-available/."
        },
        "certbot": {
            "beginner": "Certbot automatically gets and installs free SSL certificates from Let's Encrypt, making your website use HTTPS.",
            "familiar": "Let's Encrypt certificate management. certonly for cert-only, --nginx/--apache for auto-config, renew for renewal."
        },
        "fail2ban-client": {
            "beginner": "Fail2ban protects your server by automatically blocking IP addresses that make too many failed login attempts.",
            "familiar": "Fail2ban management. status for overview, status jail for specific jail, set jail banip/unbanip for manual management."
        },
        "cURL -X POST": {
            "beginner": "This sends data to a web server using the POST method, like submitting a form. You usually include data with -d and set Content-Type with -H.",
            "familiar": "HTTP POST request. -H 'Content-Type: application/json' -d '{\"key\":\"value\"}'. Common for API testing."
        },
        "git flow": {
            "beginner": "Git Flow is a branching strategy that provides a structured way to manage features, releases, and hotfixes in your project.",
            "familiar": "Git branching model tool. feature/release/hotfix start/finish. Manages develop/main branches. Alternative: trunk-based development."
        },
        "gzip": {
            "beginner": "This compresses a file to make it smaller. The original file is replaced with a .gz compressed version. Use gunzip to decompress.",
            "familiar": "File compression. -d to decompress (or gunzip), -k to keep original, -9 for max compression, -l to list info."
        },
        "gunzip": {
            "beginner": "This decompresses a .gz file back to its original form. Same as 'gzip -d'.",
            "familiar": "Decompress .gz files. Same as gzip -d. -k to keep compressed file. -l to list archive info."
        },
        "bzip2": {
            "beginner": "This compresses files using bzip2 compression, which creates smaller files than gzip but takes longer. Use bunzip2 to decompress.",
            "familiar": "File compression (better ratio than gzip). -d to decompress (or bunzip2), -k to keep original, -9 for max compression."
        },
        "xz": {
            "beginner": "This compresses files using xz compression, which creates the smallest files but is the slowest. Use unxz to decompress.",
            "familiar": "File compression (best ratio). -d to decompress (or unxz), -k to keep original, -T for threads, -9 for max compression."
        },
        "7z": {
            "beginner": "This creates and extracts 7-Zip archives, which often achieve better compression than zip files.",
            "familiar": "7-Zip archiver. a to add, x to extract, l to list. Supports many formats. Better compression than zip."
        },
        "unrar": {
            "beginner": "This extracts files from .rar archive files. Use 'unrar x file.rar' to extract with full paths.",
            "familiar": "Extract RAR archives. x for extract with paths, e for extract flat, l for list contents."
        },
        "ar": {
            "beginner": "This creates and manages archive files, mainly used for creating static libraries (.a files) in C/C++ development.",
            "familiar": "Archive utility. rcs for create/update static library, t for list contents, x for extract."
        },
        "upx": {
            "beginner": "UPX compresses executable programs to make them smaller. The program still works normally but takes up less disk space.",
            "familiar": "Executable packer. --best for max compression, -d to decompress. Reduces binary size. May trigger antivirus false positives."
        },
        "task": {
            "beginner": "Task (Taskfile) is a modern alternative to Make. It runs tasks defined in a Taskfile.yml and is simpler than Makefiles.",
            "familiar": "Task runner. Defined in Taskfile.yml. task name to run, -l to list. YAML-based alternative to Make."
        },
        "just": {
            "beginner": "just is a command runner similar to Make but simpler. It runs recipes defined in a justfile.",
            "familiar": "Command runner. Defined in justfile. Simpler than Make, no build system. Supports variables, arguments, conditionals."
        },
        "act": {
            "beginner": "This lets you run GitHub Actions workflows locally on your computer before pushing them to GitHub.",
            "familiar": "Run GitHub Actions locally. act -l to list workflows, act for default event, -j for specific job. Uses Docker."
        },
        "pre-commit": {
            "beginner": "This runs automated checks on your code every time you make a git commit, catching mistakes before they enter your codebase.",
            "familiar": "Git pre-commit hook framework. install to set up, run --all-files to check all. Config in .pre-commit-config.yaml."
        },
        "lazygit": {
            "beginner": "This is a beautiful terminal interface for Git. It makes staging, committing, branching, and merging much more visual and intuitive.",
            "familiar": "Terminal UI for git. Interactive staging, branch management, stash, rebase. Keyboard-driven. Much faster than CLI git."
        },
        "lazydocker": {
            "beginner": "This is a terminal interface for Docker that shows all your containers, images, and volumes in an easy-to-use dashboard.",
            "familiar": "Terminal UI for Docker. Live container stats, logs, management. Keyboard-driven dashboard for Docker resources."
        },
        "k9s": {
            "beginner": "This is a terminal interface for Kubernetes that makes managing your cluster much easier than typing kubectl commands.",
            "familiar": "Terminal UI for Kubernetes. Interactive pod/service/deployment management. :command for resources, / for filter."
        },
        "stern": {
            "beginner": "Stern lets you tail logs from multiple Kubernetes pods at once, with each pod's output in a different color.",
            "familiar": "Multi-pod log tailing for Kubernetes. stern pod-query for regex matching, --since for time window, -c for container filter."
        },
        "skaffold": {
            "beginner": "Skaffold automates the development workflow for Kubernetes \u2014 it builds, pushes, and deploys your app every time you save a file.",
            "familiar": "Kubernetes development workflow. dev for continuous development, run for one-off deploy, build for image build only."
        },
        "minikube": {
            "beginner": "Minikube runs a small Kubernetes cluster on your own computer for learning and development. 'minikube start' gets it running.",
            "familiar": "Local Kubernetes cluster. start/stop/delete/dashboard. Supports multiple drivers (docker, virtualbox). addons for extensions."
        },
        "kind": {
            "beginner": "kind (Kubernetes IN Docker) creates Kubernetes clusters using Docker containers. Lightweight and fast for testing.",
            "familiar": "Kubernetes in Docker. create/delete cluster, get clusters, load docker-image. Config via YAML for multi-node clusters."
        },
        "kubectx": {
            "beginner": "This lets you quickly switch between different Kubernetes clusters and namespaces without typing long kubectl commands.",
            "familiar": "Fast Kubernetes context/namespace switching. kubectx for context, kubens for namespace. Interactive with fzf."
        },
        "kustomize": {
            "beginner": "Kustomize lets you customize Kubernetes YAML configurations without modifying the original files, using patches and overlays.",
            "familiar": "Kubernetes configuration customization. kustomize build for output, kubectl apply -k for direct apply. Patches and overlays."
        },
        "istioctl": {
            "beginner": "Istio manages network traffic between microservices in Kubernetes. istioctl is its command-line tool for installation and debugging.",
            "familiar": "Istio service mesh CLI. install/verify-install/analyze/proxy-config. Manages traffic routing, security, observability."
        },
        "prometheus": {
            "beginner": "Prometheus collects and stores metrics (measurements) from your applications and servers for monitoring and alerting.",
            "familiar": "Metrics monitoring system. PromQL for queries, --config.file for config. Scrapes /metrics endpoints. Pairs with Grafana."
        },
        "grafana-cli": {
            "beginner": "Grafana creates beautiful dashboards for monitoring your applications. The CLI manages plugins and server settings.",
            "familiar": "Grafana management CLI. plugins install/list, admin reset-admin-password. Dashboards typically managed via web UI."
        },
        "ansible-playbook": {
            "beginner": "This runs an Ansible playbook \u2014 a file that describes a set of tasks to automate on remote servers, like installing software or configuring settings.",
            "familiar": "Execute Ansible playbook. -i for inventory, -e for extra vars, --check for dry run, --limit for host subset."
        },
        "curl -I": {
            "beginner": "This shows just the HTTP headers from a URL without downloading the body. Useful for checking server type, caching, and redirects.",
            "familiar": "Fetch HTTP headers only. Shows status code, content-type, cache headers, etc. -L to follow redirects."
        },
        "curl -o": {
            "beginner": "This downloads a file from a URL and saves it with the name you specify. 'curl -o output.txt https://example.com' saves the page to output.txt.",
            "familiar": "Download and save to file. -O to use remote filename, -L to follow redirects, -C - to resume interrupted download."
        },
        "whois": {
            "beginner": "This looks up registration information about a domain name, showing who owns it, when it was registered, and when it expires.",
            "familiar": "Query domain registration info. Shows registrar, nameservers, expiry date, contact info (if not privacy-protected)."
        },
        "htop -t": {
            "beginner": "This shows running processes in a tree view, so you can see which programs started other programs (parent-child relationships).",
            "familiar": "htop in tree view mode. Shows process hierarchy. F5 to toggle tree mode interactively."
        },
        "iotop": {
            "beginner": "This shows which programs are reading from or writing to your disk, like a task manager focused on disk activity.",
            "familiar": "I/O monitoring. Shows per-process disk read/write. -o for only active processes, -a for accumulated. Needs root."
        },
        "nethogs": {
            "beginner": "This shows which programs are using the most network bandwidth in real-time, like a task manager for internet usage.",
            "familiar": "Per-process network bandwidth monitor. Groups by process, shows upload/download. Needs root."
        },
        "pgrep": {
            "beginner": "This finds the process ID (PID) of running programs by name. 'pgrep firefox' shows the PID of Firefox.",
            "familiar": "Find processes by name/attributes. -l for name, -f for full command, -u for user. Returns PIDs."
        },
        "pkill": {
            "beginner": "This stops programs by name instead of PID. 'pkill firefox' stops all Firefox processes. Easier than finding the PID first.",
            "familiar": "Signal processes by name. -9 for force kill, -f for full command match, -u for user filter."
        },
        "killall": {
            "beginner": "This stops all processes with a given name. 'killall node' stops all Node.js processes. Be careful not to kill important processes.",
            "familiar": "Kill processes by name. -9 for SIGKILL, -I for case-insensitive, -w to wait for termination."
        },
        "fuser": {
            "beginner": "This shows which processes are using a specific file or port. 'fuser -n tcp 8080' shows what's using port 8080.",
            "familiar": "Identify processes using files/sockets. -k to kill, -n tcp for network, -m for mountpoint. Alternative to lsof."
        },
        "vmstat": {
            "beginner": "This shows system performance statistics including memory, CPU, and disk activity. Run 'vmstat 1' for continuous updates every second.",
            "familiar": "Virtual memory statistics. Shows procs, memory, swap, io, system, cpu. vmstat N for interval. -s for summary."
        },
        "iostat": {
            "beginner": "This shows CPU and disk I/O statistics, helping you understand if your disk or CPU is the bottleneck.",
            "familiar": "CPU and I/O statistics. -x for extended, -d for disk only, -c for CPU only. iostat N for interval."
        },
        "mpstat": {
            "beginner": "This shows CPU usage statistics for each processor core, helping identify if one core is overloaded.",
            "familiar": "Per-processor statistics. -P ALL for all CPUs, mpstat N for interval. Part of sysstat package."
        },
        "sar": {
            "beginner": "This collects and reports system activity data (CPU, memory, disk, network) over time. Useful for historical performance analysis.",
            "familiar": "System Activity Reporter. -u for CPU, -r for memory, -d for disk, -n for network. Collects data via sadc/cron."
        },
        "perf": {
            "beginner": "This is a performance analysis tool for Linux that can profile your programs to find which parts are slowest.",
            "familiar": "Linux performance tool. perf stat for counters, perf record/report for profiling, perf top for live. Hardware counters."
        },
        "last": {
            "beginner": "This shows who has logged into the system recently and when. 'last' shows login history for all users.",
            "familiar": "Show login history. last -n N for recent, last username for specific user, lastb for failed logins (needs root)."
        },
        "w": {
            "beginner": "This shows who is currently logged into the system and what they're doing, including their CPU usage.",
            "familiar": "Show logged-in users and activity. Shows user, TTY, login time, idle time, current command."
        },
        "who": {
            "beginner": "This shows which users are currently logged into the system.",
            "familiar": "Show who is logged in. -b for last boot time, -r for run level. Similar to w but less detail."
        },
        "finger": {
            "beginner": "This shows information about a user account, including their real name, login time, and directory.",
            "familiar": "User information lookup. Shows name, directory, shell, login time, mail status. Not installed by default on most systems."
        },
        "chroot": {
            "beginner": "This runs a command with a different root directory, creating an isolated environment. Used for system recovery and security.",
            "familiar": "Change root directory. Creates isolated filesystem view. Used for system recovery and minimal containers."
        },
        "sysctl": {
            "beginner": "This views and changes kernel parameters that control how your operating system behaves at a low level.",
            "familiar": "Configure kernel parameters at runtime. -a to list all, -w to write, -p to load from file. Persistent in /etc/sysctl.conf."
        },
        "ulimit": {
            "beginner": "This shows or sets limits on system resources (like max open files or memory) for the current shell session.",
            "familiar": "Set/show resource limits. -n for max open files, -u for max processes, -a for all limits. -H/-S for hard/soft."
        },
        "lscpu": {
            "beginner": "This shows detailed information about your CPU(s), including the model, number of cores, speed, and architecture.",
            "familiar": "Display CPU architecture info. Shows cores, threads, caches, model, flags. Reads from /proc/cpuinfo and sysfs."
        },
        "lsusb": {
            "beginner": "This lists all USB devices connected to your computer, showing what they are and which bus they're on.",
            "familiar": "List USB devices. -v for verbose, -t for tree. Shows vendor:product IDs useful for driver troubleshooting."
        },
        "lspci": {
            "beginner": "This lists all PCI devices in your computer, including graphics cards, network adapters, and other hardware.",
            "familiar": "List PCI devices. -v for verbose, -k for kernel drivers, -nn for vendor/device codes."
        },
        "lshw": {
            "beginner": "This shows a comprehensive list of all hardware in your computer, including CPU, memory, disk, and network devices.",
            "familiar": "List hardware configuration. -short for summary, -class for specific type (memory, disk, network). Needs root for full info."
        },
        "hwinfo": {
            "beginner": "This displays detailed hardware information about your system. Similar to lshw but sometimes provides more detail.",
            "familiar": "Detailed hardware info. --short for summary, --disk/--cpu/--memory for specific hardware. SUSE-originated tool."
        },
        "dmidecode": {
            "beginner": "This reads hardware information from your computer's BIOS/UEFI, showing details about memory, motherboard, and BIOS version.",
            "familiar": "Read DMI/SMBIOS data. -t for type (memory, bios, processor). Needs root. Shows hardware details from firmware."
        },
        "smartctl": {
            "beginner": "This checks the health of your hard drives and SSDs, showing if they're developing problems before they fail.",
            "familiar": "S.M.A.R.T. disk monitoring. -a for all info, -H for health, -t for self-test. Part of smartmontools."
        },
        "hdparm": {
            "beginner": "This gets or sets hard drive parameters like read speed and power management settings.",
            "familiar": "Hard drive parameters. -Tt for benchmarking, -I for drive info, -S for standby timeout. For SATA/IDE drives."
        },
        "sensors": {
            "beginner": "This shows temperature readings from your CPU, motherboard, and other components. Helps check if your computer is overheating.",
            "familiar": "Hardware temperature monitoring. Run sensors-detect first. Shows CPU/GPU/board temps, fan speeds. From lm-sensors."
        },
        "acpi": {
            "beginner": "This shows battery status and thermal information on laptops. 'acpi -b' shows battery level.",
            "familiar": "Show ACPI info. -b for battery, -t for thermal, -a for AC adapter. Useful for laptop battery monitoring."
        },
        "udevadm": {
            "beginner": "This manages the Linux device manager (udev) that handles hardware devices being plugged in and removed.",
            "familiar": "udev management tool. info for device info, monitor for events, trigger for re-processing rules."
        },
        "modprobe": {
            "beginner": "This loads or unloads kernel modules (drivers) in Linux. Used to add support for hardware or features.",
            "familiar": "Load/unload kernel modules. -r to remove, --show-depends for dependencies. Loads from /lib/modules/."
        },
        "lsmod": {
            "beginner": "This shows all kernel modules (drivers) currently loaded in your Linux system.",
            "familiar": "List loaded kernel modules. Shows module name, size, and dependencies. Used for hardware troubleshooting."
        },
        "depmod": {
            "beginner": "This generates a dependency list for kernel modules, so the system knows which modules need other modules to work.",
            "familiar": "Generate module dependency files. Usually run automatically. -a for all modules in current kernel."
        },
        "insmod": {
            "beginner": "This loads a kernel module directly from a file. Lower-level than modprobe and doesn't handle dependencies.",
            "familiar": "Insert kernel module. Lower-level than modprobe, no dependency resolution. Use modprobe instead in most cases."
        },
        "rmmod": {
            "beginner": "This removes a loaded kernel module. Use 'modprobe -r' instead as it handles dependencies properly.",
            "familiar": "Remove kernel module. No dependency handling (use modprobe -r instead). -f for force removal."
        },
        "env | grep": {
            "beginner": "This shows environment variables that match a search term. 'env | grep PATH' shows your PATH variable.",
            "familiar": "Filter environment variables. Common: env | grep -i proxy for proxy settings, env | grep PATH for path."
        },
        "chmod +x": {
            "beginner": "This makes a file executable, meaning you can run it as a program. Required before you can run shell scripts with ./script.sh.",
            "familiar": "Add execute permission. chmod +x script.sh then ./script.sh to run. Same as chmod a+x."
        },
        "tar -xzf": {
            "beginner": "This extracts files from a compressed .tar.gz archive. Like unzipping a file. -x extracts, -z handles gzip, -f specifies the file.",
            "familiar": "Extract gzipped tar archive. -v for verbose, -C for target directory. For .tar.bz2 use -xjf, for .tar.xz use -xJf."
        },
        "tar -czf": {
            "beginner": "This creates a compressed .tar.gz archive from files and folders. Like zipping files together.",
            "familiar": "Create gzipped tar archive. tar -czf archive.tar.gz files/dirs. -v for verbose. For .tar.bz2 use -cjf."
        },
        "ssh-agent": {
            "beginner": "This manages your SSH keys in memory so you don't have to type your key passphrase every time you connect to a server.",
            "familiar": "SSH key agent. eval $(ssh-agent) to start, ssh-add to add keys, ssh-add -l to list. Manages key passphrases."
        },
        "ssh-add": {
            "beginner": "This adds your SSH key to the ssh-agent so you can connect to remote servers without typing your passphrase each time.",
            "familiar": "Add SSH keys to agent. -l to list, -D to remove all, -t for lifetime. Works with ssh-agent."
        },
        "sftp": {
            "beginner": "This is a secure way to transfer files to and from a remote server. It works like a file manager over an SSH connection.",
            "familiar": "Secure file transfer. Interactive: get/put/ls/cd. Batch: -b batchfile. Alternative to scp with interactive mode."
        },
        "resolvectl": {
            "beginner": "This shows and manages DNS settings on modern Linux systems using systemd-resolved.",
            "familiar": "systemd-resolved management. status for current config, query for lookups, flush-caches for DNS cache clear."
        },
        "ip netns": {
            "beginner": "This manages network namespaces \u2014 isolated network environments used by containers and for testing.",
            "familiar": "Network namespace management. add/list/delete/exec. Used for network isolation in containers."
        },
        "brctl": {
            "beginner": "This manages network bridges that connect multiple network interfaces together, like a virtual network switch.",
            "familiar": "Linux bridge management (legacy). addbr/delbr/addif/delif/show. Modern: ip link add type bridge."
        },
        "wg": {
            "beginner": "This manages WireGuard VPN connections. WireGuard is a fast, modern VPN that's simpler than older VPN solutions.",
            "familiar": "WireGuard management. wg show for status, wg-quick up/down for tunnel management. Config in /etc/wireguard/."
        },
        "certutil": {
            "beginner": "This manages certificates in the NSS security database, used by browsers and some applications for SSL/TLS.",
            "familiar": "NSS certificate database tool. -L to list, -A to add, -D to delete. Used for browser certificate management."
        },
        "systemd-run": {
            "beginner": "This runs a command as a transient systemd service, giving it process management and resource control capabilities.",
            "familiar": "Run as transient service. --scope for scope unit, --user for user session, --timer-property for scheduling."
        },
        "loginctl": {
            "beginner": "This shows information about current user sessions and can lock, terminate, or manage login sessions.",
            "familiar": "systemd login manager control. list-sessions/show-session/terminate-session. manage user sessions and seats."
        },
        "xrandr": {
            "beginner": "This manages display resolution and arrangement on Linux. You can change resolution, rotation, and multi-monitor setup.",
            "familiar": "X display configuration. --output for display, --mode for resolution, --rate for refresh, --pos for position."
        },
        "adb": {
            "beginner": "Android Debug Bridge lets you communicate with Android devices from your computer for development, debugging, and file transfer.",
            "familiar": "Android Debug Bridge. devices to list, shell for remote shell, install for APK, push/pull for files, logcat for logs."
        },
        "fastboot": {
            "beginner": "This manages Android devices in bootloader mode. Used for flashing firmware, unlocking bootloaders, and recovery.",
            "familiar": "Android bootloader interface. devices to list, flash for partitions, oem unlock for bootloader. Used for ROM flashing."
        },
        "convert": {
            "beginner": "This converts images between formats (PNG, JPG, etc.) and can resize, crop, and modify images from the command line.",
            "familiar": "ImageMagick image conversion. convert input.png -resize 50% output.jpg. Supports batch processing and complex operations."
        },
        "ffmpeg": {
            "beginner": "This converts and processes video and audio files. It can change formats, resize videos, extract audio, and much more.",
            "familiar": "Multimedia framework. -i input, -c:v codec, -c:a codec, -vf for video filters. Extremely versatile for media processing."
        },
        "sox": {
            "beginner": "SoX is a command-line audio tool that can convert, trim, mix, and add effects to audio files.",
            "familiar": "Sound processing tool. sox input output for convert, trim/fade/reverb for effects, play/rec for playback/recording."
        },
        "pandoc": {
            "beginner": "Pandoc converts documents between formats \u2014 Markdown to PDF, HTML to Word, LaTeX to EPUB, and many more.",
            "familiar": "Universal document converter. -f from format, -t to format, -o output file. Supports Markdown, HTML, LaTeX, DOCX, PDF."
        },
        "wkhtmltopdf": {
            "beginner": "This converts HTML web pages to PDF files. You can save any webpage as a PDF from the command line.",
            "familiar": "HTML to PDF converter. Uses WebKit rendering. --page-size, --orientation, --header-html for customization."
        },
        "ghostscript": {
            "beginner": "Ghostscript processes PDF and PostScript files. It can merge, split, compress, and convert PDF documents.",
            "familiar": "PDF/PostScript interpreter. gs for processing. Common: PDF compression, merge, page extraction. Used by many tools internally."
        },
        "tesseract": {
            "beginner": "Tesseract reads text from images (OCR). It can extract text from screenshots, scanned documents, and photos.",
            "familiar": "OCR engine. tesseract image output -l lang. --oem for engine mode, --psm for page segmentation mode."
        },
        "dot": {
            "beginner": "This creates diagrams and graphs from text descriptions. Part of Graphviz. Write relationships in a .dot file and it draws the picture.",
            "familiar": "Graphviz graph renderer. dot -Tpng input.dot -o output.png. Supports svg, pdf, png. Also: neato, fdp, circo layouts."
        },
        "gnuplot": {
            "beginner": "This creates charts and graphs from data. You can make line plots, scatter plots, and more from the command line.",
            "familiar": "Data plotting tool. Interactive or script-based. Supports 2D/3D plots, many output formats. set terminal for output type."
        },
        "inotifywait": {
            "beginner": "This watches files or directories for changes and triggers actions when files are modified, created, or deleted.",
            "familiar": "Filesystem event monitor. -m for continuous, -r for recursive, -e for specific events. Part of inotify-tools."
        },
        "entr": {
            "beginner": "This runs a command whenever files change. 'ls *.py | entr python test.py' re-runs tests whenever you save a Python file.",
            "familiar": "Run command on file change. ls files | entr command. -r for restart, -c for clear screen. Great for dev workflows."
        },
        "direnv": {
            "beginner": "This automatically loads and unloads environment variables when you enter and leave a directory. Great for project-specific settings.",
            "familiar": "Directory-based env management. .envrc for per-directory vars. direnv allow to trust. Auto-loads/unloads on cd."
        },
        "asdf": {
            "beginner": "asdf manages multiple versions of programming languages. Use it to install different versions of Python, Node.js, Ruby, and more.",
            "familiar": "Multi-runtime version manager. plugin add/install/global/local. .tool-versions for per-project versions. Replaces nvm/rbenv/pyenv."
        },
        "nvm": {
            "beginner": "nvm manages multiple versions of Node.js. 'nvm install 18' installs Node 18, 'nvm use 18' switches to it.",
            "familiar": "Node Version Manager. install/use/ls/alias for version management. .nvmrc for per-project versions."
        },
        "pyenv": {
            "beginner": "pyenv manages multiple versions of Python. 'pyenv install 3.11' installs Python 3.11, 'pyenv global 3.11' sets it as default.",
            "familiar": "Python version manager. install/global/local/versions. .python-version for per-project. Shims-based path management."
        },
        "rbenv": {
            "beginner": "rbenv manages multiple versions of Ruby. Install different Ruby versions and switch between them per-project.",
            "familiar": "Ruby version manager. install/global/local/versions. .ruby-version for per-project. Shims-based. Uses ruby-build plugin."
        },
        "mise": {
            "beginner": "mise (formerly rtx) is a modern tool version manager that replaces asdf, nvm, pyenv, and similar tools with one fast tool.",
            "familiar": "Polyglot runtime manager. install/use/ls for versions. .mise.toml for config. Drop-in asdf replacement, written in Rust."
        },
        "dotenv": {
            "beginner": "This loads environment variables from a .env file into your shell session. Useful for managing project-specific configuration.",
            "familiar": "Load .env files into shell. Various implementations exist. Common in development workflows. Pairs with direnv."
        },
        "pass": {
            "beginner": "pass is a simple password manager for the command line. It stores passwords encrypted with GPG in simple text files.",
            "familiar": "Unix password manager. init/insert/show/generate/edit. GPG-encrypted, git-backed. pass otp for TOTP support."
        },
        "age": {
            "beginner": "age is a simple, modern encryption tool. It encrypts and decrypts files with a passphrase or public key.",
            "familiar": "Simple file encryption. -e for encrypt, -d for decrypt, -p for passphrase, -R for recipient file. Modern alternative to GPG."
        },
        "sops": {
            "beginner": "SOPS encrypts specific values in config files (YAML, JSON, ENV) while leaving keys readable. Great for storing secrets in git.",
            "familiar": "Secrets management for config files. Encrypts values, not keys. Supports GPG, AWS KMS, age. sops -e/-d for encrypt/decrypt."
        },
        "vault": {
            "beginner": "HashiCorp Vault securely stores and controls access to secrets like API keys, passwords, and certificates.",
            "familiar": "Secrets management. kv put/get for key-value, token/userpass/ldap for auth. Dynamic secrets for databases/cloud."
        }
    },
    "error_patterns": {
        "command not found": {
            "pattern": "command not found|is not recognized",
            "beginner": "Your computer doesn't recognize this command. This usually means: (1) the program isn't installed yet, (2) you misspelled the command, or (3) the program isn't in your system's PATH (the list of places your computer looks for programs).",
            "familiar": "Command not in PATH. Check spelling, verify installation, or add the binary's directory to your PATH."
        },
        "permission denied": {
            "pattern": "[Pp]ermission denied",
            "beginner": "You don't have the right permissions to do this. It's like trying to open a locked door. You might need to use 'sudo' (administrator mode) or change the file's permissions with 'chmod'.",
            "familiar": "Insufficient permissions. Use sudo for elevated access, or chmod/chown to modify file permissions."
        },
        "no such file or directory": {
            "pattern": "[Nn]o such file or directory",
            "beginner": "The file or folder you're trying to use doesn't exist at the location you specified. Double-check the spelling and make sure you're in the right directory (use 'pwd' to check where you are and 'ls' to see what's available).",
            "familiar": "File/directory not found. Check path, spelling, and current working directory. Use tab completion to avoid typos."
        },
        "segmentation fault": {
            "pattern": "[Ss]egmentation fault|SIGSEGV|segfault",
            "beginner": "The program crashed because it tried to access memory it wasn't allowed to use. This is a bug in the program's code \u2014 it's not something you did wrong. If it's your code, look for issues with arrays, pointers, or null values.",
            "familiar": "SIGSEGV \u2014 invalid memory access. Common causes: null pointer dereference, buffer overflow, stack overflow, use-after-free."
        },
        "connection refused": {
            "pattern": "[Cc]onnection refused|ECONNREFUSED",
            "beginner": "Your computer tried to connect to another computer or service, but the connection was rejected. This usually means the service you're trying to reach isn't running or is on a different port/address.",
            "familiar": "Target service not listening on the specified port. Verify the service is running and check host:port configuration."
        },
        "syntax error": {
            "pattern": "[Ss]yntax[Ee]rror|syntax error",
            "beginner": "There's a typo or formatting mistake in your code or command. The computer can't understand what you wrote because it doesn't follow the expected rules. Check for missing brackets, quotes, colons, or semicolons.",
            "familiar": "Invalid syntax in code/command. Check for unclosed brackets/quotes, missing operators, or incorrect statement structure."
        },
        "module not found": {
            "pattern": "ModuleNotFoundError|Cannot find module|No module named",
            "beginner": "Your code is trying to use a package/library that isn't installed. You need to install it first using 'pip install <package_name>' (for Python) or 'npm install <package_name>' (for JavaScript).",
            "familiar": "Missing dependency. Install with pip/npm/yarn. Check virtual environment activation and verify package name."
        },
        "port in use": {
            "pattern": "[Aa]ddress already in use|EADDRINUSE|port.*already.*in.*use",
            "beginner": "Another program is already using the network port your app needs. It's like two radio stations trying to broadcast on the same frequency. You need to either stop the other program or use a different port number.",
            "familiar": "Port conflict. Find the process: lsof -i :PORT or netstat -tlnp. Kill it or use a different port."
        },
        "out of memory": {
            "pattern": "[Oo]ut of memory|MemoryError|ENOMEM|OOMKilled|JavaScript heap out of memory",
            "beginner": "Your computer ran out of available memory (RAM) while running this program. The program was using too much memory and the system had to stop it. Try closing other applications or processing less data at once.",
            "familiar": "OOM condition. Increase memory limits, optimize data structures, process in chunks, or add swap space."
        },
        "timeout": {
            "pattern": "[Tt]imeout|timed out|ETIMEDOUT|ESOCKETTIMEDOUT",
            "beginner": "The operation took too long and was stopped. This usually happens with network connections when a server is too slow to respond, is down, or can't be reached.",
            "familiar": "Operation exceeded time limit. Check network connectivity, server availability, and consider increasing timeout values."
        },
        "disk space": {
            "pattern": "[Nn]o space left on device|ENOSPC|disk full",
            "beginner": "Your computer's hard drive is full. You need to free up space by deleting files you don't need, emptying the trash, or clearing temporary files and caches.",
            "familiar": "Disk full. Check usage with df -h, find large files with du -sh *, clear logs/caches/tmp files."
        },
        "git merge conflict": {
            "pattern": "CONFLICT.*Merge conflict|merge conflict|Automatic merge failed",
            "beginner": "Two people (or two branches) changed the same part of the same file differently, and Git doesn't know which version to keep. You need to open the file, look for the conflict markers (<<<<<<, ======, >>>>>>), decide which changes to keep, then save and commit.",
            "familiar": "Merge conflict. Edit conflicted files (look for <<<<<<< markers), resolve differences, then git add and git commit."
        },
        "ssl certificate": {
            "pattern": "SSL.*certificate|CERT_|certificate verify failed|SSL_ERROR",
            "beginner": "There's a problem with the security certificate of the website or server you're trying to connect to. This could mean the certificate is expired, self-signed, or the connection isn't secure.",
            "familiar": "SSL/TLS certificate issue. Check cert expiry, CA trust chain, or system clock. Avoid --insecure in production."
        },
        "import error": {
            "pattern": "ImportError|cannot import name",
            "beginner": "Your code is trying to import something that doesn't exist or can't be found in the package. This might mean the package version is wrong, or you're trying to import a function/class that doesn't exist in that package.",
            "familiar": "Import failure. Check package version compatibility, verify import path, ensure no circular imports."
        },
        "type error": {
            "pattern": "TypeError",
            "beginner": "Your code tried to do something with the wrong type of data. For example, trying to add a number and a piece of text together, or calling something that isn't a function. Check what types of values your variables actually contain.",
            "familiar": "Type mismatch. Check argument types, verify function signatures, and ensure proper type conversions."
        },
        "key error": {
            "pattern": "KeyError",
            "beginner": "Your code tried to look up a key in a dictionary (a collection of key-value pairs) that doesn't exist. It's like looking for a word in a dictionary that isn't there. Check for typos in the key name or use .get() for safe access.",
            "familiar": "Missing dictionary key. Use .get(key, default) for safe access, or check with 'if key in dict' first."
        },
        "file exists": {
            "pattern": "FileExistsError|EEXIST|already exists",
            "beginner": "You're trying to create a file or folder that already exists. You either need to choose a different name, delete the existing one first, or use a flag that allows overwriting.",
            "familiar": "Path already exists. Use os.path.exists() to check first, or use appropriate overwrite flags."
        },
        "recursion error": {
            "pattern": "RecursionError|maximum recursion depth|Maximum call stack size exceeded",
            "beginner": "A function in your code keeps calling itself over and over in an endless loop until the computer runs out of space to track all the calls. You need to add a condition that tells the function when to stop calling itself.",
            "familiar": "Stack overflow from infinite recursion. Add/fix base case, or convert to iterative approach. Can increase limit with sys.setrecursionlimit()."
        },
        "npm error": {
            "pattern": "npm ERR!|npm WARN",
            "beginner": "The Node.js package manager (npm) ran into a problem. Read the error message carefully \u2014 it usually tells you what went wrong, like a missing package, version conflict, or network issue.",
            "familiar": "npm error. Common fixes: rm -rf node_modules && npm install, npm cache clean --force, check package.json for version conflicts."
        },
        "pip error": {
            "pattern": "pip.*error|Could not install|Failed building wheel",
            "beginner": "Python's package installer (pip) had trouble installing something. This could be because: the package name is wrong, you need system libraries installed first, or there's a Python version mismatch.",
            "familiar": "pip install failure. Check package name, ensure build tools are installed (build-essential), verify Python version compatibility."
        },
        "docker daemon": {
            "pattern": "Cannot connect to the Docker daemon|docker daemon.*not running|Is the docker daemon running",
            "beginner": "Docker isn't running on your computer. You need to start the Docker application first before you can use Docker commands. On Linux, try 'sudo systemctl start docker'.",
            "familiar": "Docker daemon not running. Start with: sudo systemctl start docker (Linux), or launch Docker Desktop (Mac/Windows)."
        },
        "docker image not found": {
            "pattern": "manifest.*not found|Error response from daemon.*not found|repository does not exist",
            "beginner": "Docker can't find the image you're trying to use. This usually means the image name is misspelled or it doesn't exist on Docker Hub.",
            "familiar": "Docker image not found in registry. Check image name/tag, verify registry URL, ensure docker login for private repos."
        },
        "docker port conflict": {
            "pattern": "port is already allocated|Bind for.*failed.*port.*already",
            "beginner": "Another program is already using the port Docker is trying to use. Either stop the other program or change the port mapping in your Docker command.",
            "familiar": "Port already bound. Use -p HOST:CONTAINER with different host port, or stop the conflicting process."
        },
        "npm peer dependency": {
            "pattern": "ERESOLVE|peer dep|Could not resolve dependency|conflicting peer dependency",
            "beginner": "npm found conflicting package versions. Some packages require specific versions of other packages. Try running 'npm install --legacy-peer-deps' to work around it.",
            "familiar": "Peer dependency conflict. Use --legacy-peer-deps or --force to bypass. Consider updating packages to compatible versions."
        },
        "npm eacces": {
            "pattern": "EACCES.*permission denied|npm ERR.*EACCES|Missing write access",
            "beginner": "npm doesn't have permission to write files. This often happens when installing global packages. Try using 'sudo' or fix npm permissions.",
            "familiar": "npm permission error. Fix: sudo chown -R $(whoami) ~/.npm, or configure npm prefix to user directory. Avoid sudo npm."
        },
        "npm enoent": {
            "pattern": "ENOENT.*package.json|npm ERR.*enoent|npm ERR.*missing script",
            "beginner": "npm can't find a required file (usually package.json). Make sure you're in the right project directory. If package.json is missing, run 'npm init'.",
            "familiar": "Missing package.json or script. Check working directory, run npm init if needed, verify script exists in package.json scripts."
        },
        "python import error": {
            "pattern": "ImportError|from.*import.*cannot|cannot import name",
            "beginner": "Python can't import something from a module. This could mean the module version is different from what you expect, or the function/class name is wrong.",
            "familiar": "Import failure. Check module version, verify function/class exists in that version, check for circular imports."
        },
        "python type error": {
            "pattern": "TypeError.*argument|TypeError.*expected|TypeError.*not.*callable|TypeError.*not supported",
            "beginner": "You passed the wrong type of data to a function. For example, passing text where a number was expected. Check the function's documentation for the correct types.",
            "familiar": "Type mismatch. Check function signature, argument types, and ensure correct data types are passed."
        },
        "python key error": {
            "pattern": "KeyError",
            "beginner": "You tried to access a key that doesn't exist in a dictionary. It's like looking up a word in a dictionary that isn't listed. Use .get() to safely handle missing keys.",
            "familiar": "Dictionary key not found. Use dict.get(key, default) for safe access, or check with 'if key in dict' first."
        },
        "python index error": {
            "pattern": "IndexError.*out of range|list index out of range",
            "beginner": "You tried to access an item at a position that doesn't exist in a list. For example, asking for item #10 in a list that only has 5 items.",
            "familiar": "List index out of bounds. Check list length, use try/except, or validate index before access."
        },
        "python attribute error": {
            "pattern": "AttributeError.*has no attribute|AttributeError.*object",
            "beginner": "You tried to use a feature that doesn't exist on this object. This often happens when a variable is a different type than you expected (like None instead of a list).",
            "familiar": "Object doesn't have requested attribute. Check object type, verify method/attribute name, handle None values."
        },
        "python value error": {
            "pattern": "ValueError.*invalid literal|ValueError.*could not convert|ValueError",
            "beginner": "A function received the right type of data but the value was wrong. For example, trying to convert the word 'hello' to a number.",
            "familiar": "Invalid value for operation. Common with type conversion, data parsing. Validate input before processing."
        },
        "python file not found": {
            "pattern": "FileNotFoundError|No such file or directory.*python",
            "beginner": "Python can't find the file you're trying to open. Check the filename spelling and make sure you're running your script from the right directory.",
            "familiar": "File path not found. Check relative vs absolute path, verify CWD with os.getcwd(), use pathlib for robust paths."
        },
        "python recursion": {
            "pattern": "RecursionError|maximum recursion depth exceeded",
            "beginner": "Your function keeps calling itself forever (or too many times). This usually means a recursive function is missing its stopping condition.",
            "familiar": "Infinite recursion or deep recursion. Add/fix base case, or increase limit with sys.setrecursionlimit() (not recommended)."
        },
        "ssl certificate": {
            "pattern": "SSL.*certificate|CERTIFICATE_VERIFY_FAILED|unable to get local issuer|self.signed",
            "beginner": "There's a problem with the security certificate. The connection might be insecure or the certificate has expired. Don't ignore SSL errors on sensitive connections.",
            "familiar": "SSL/TLS certificate verification failure. Check cert expiry, CA trust store, clock accuracy. Avoid disabling verification in production."
        },
        "dns resolution": {
            "pattern": "Could not resolve host|Name or service not known|NXDOMAIN|getaddrinfo.*failed",
            "beginner": "Your computer can't find the server you're trying to connect to. Check your internet connection and make sure the address is spelled correctly.",
            "familiar": "DNS resolution failure. Check /etc/resolv.conf, try alternate DNS (8.8.8.8), verify hostname, check network connectivity."
        },
        "cors error": {
            "pattern": "CORS|Access-Control-Allow-Origin|blocked by CORS|Cross-Origin",
            "beginner": "The web browser blocked a request to a different website for security. The server needs to allow your website to access its data by adding CORS headers.",
            "familiar": "Cross-Origin Resource Sharing error. Server must include Access-Control-Allow-Origin header. Configure CORS middleware on backend."
        },
        "json parse error": {
            "pattern": "JSON.*parse|Unexpected token|JSON.parse|SyntaxError.*JSON|json.decoder.JSONDecodeError",
            "beginner": "The data isn't valid JSON format. This usually means extra commas, missing quotes, or the response isn't JSON at all (maybe HTML or plain text).",
            "familiar": "Invalid JSON. Check for trailing commas, single quotes (use double), ensure response is actually JSON, validate with jsonlint."
        },
        "webpack build error": {
            "pattern": "Module build failed|webpack.*error|Module not found.*webpack|Cannot resolve module",
            "beginner": "Webpack (the bundler for your web project) couldn't build your code. Usually a missing module, wrong import path, or missing loader configuration.",
            "familiar": "Webpack build failure. Check module paths, install missing loaders/plugins, verify webpack.config.js, check import paths."
        },
        "typescript error": {
            "pattern": "TS\\d{4}|error TS|Type.*is not assignable|Property.*does not exist on type",
            "beginner": "TypeScript found a type mismatch in your code. You're using a value in a way that doesn't match its expected type. Check the variable types.",
            "familiar": "TypeScript type error. Check type annotations, use proper generics, consider type assertions or type guards."
        },
        "git authentication": {
            "pattern": "Authentication failed|fatal.*authentication|Support for password authentication was removed|Permission denied.*publickey",
            "beginner": "Git couldn't verify your identity. If using GitHub, you likely need to use a personal access token or SSH key instead of a password.",
            "familiar": "Git auth failure. Use SSH keys or personal access token. GitHub removed password auth. Check git remote URL and credentials."
        },
        "git detached head": {
            "pattern": "detached HEAD|HEAD is now at|You are in.*detached HEAD",
            "beginner": "You're looking at an old version of your code but aren't on any branch. Any commits you make might get lost. Use 'git checkout main' to get back to a branch.",
            "familiar": "Detached HEAD state. Create branch to save work: git checkout -b new-branch. Or switch to existing branch."
        },
        "kubernetes crashloopbackoff": {
            "pattern": "CrashLoopBackOff|Back-off restarting failed container",
            "beginner": "Your application in Kubernetes keeps crashing and restarting. Check the application logs with 'kubectl logs' to see why it's failing.",
            "familiar": "Container repeatedly crashing. Check: kubectl logs pod-name --previous, kubectl describe pod, verify image/command/env."
        },
        "kubernetes imagepullbackoff": {
            "pattern": "ImagePullBackOff|ErrImagePull|Failed to pull image",
            "beginner": "Kubernetes can't download the Docker image for your application. Check that the image name is correct and that you have access to it.",
            "familiar": "Image pull failure. Check image name/tag, registry authentication, imagePullSecrets configuration, network connectivity."
        },
        "kubernetes oomkilled": {
            "pattern": "OOMKilled|memory.*limit|Killed.*out of memory",
            "beginner": "Your application used too much memory and was killed. You need to either increase the memory limit or make your application use less memory.",
            "familiar": "Out of memory kill. Increase resources.limits.memory, profile memory usage, check for memory leaks."
        },
        "rust borrow checker": {
            "pattern": "cannot borrow.*as mutable|value used here after move|does not live long enough|borrowed value does not",
            "beginner": "Rust's ownership system detected a potential memory safety issue. This is Rust protecting you from bugs. Read the error carefully \u2014 it usually explains exactly what to fix.",
            "familiar": "Borrow checker error. Review ownership, use references (&/&mut), consider Clone, Rc, or restructuring code."
        },
        "go unused import": {
            "pattern": "imported and not used|declared and not used",
            "beginner": "Go doesn't allow unused imports or variables. Either use them or remove them. This is a strict rule in Go.",
            "familiar": "Go requires all imports/variables to be used. Remove unused ones, or use _ for intentional discard."
        },
        "java null pointer": {
            "pattern": "NullPointerException|java.lang.NullPointerException",
            "beginner": "Your Java program tried to use something that doesn't exist (null). A variable was expected to contain an object but was empty. Check where the null value comes from.",
            "familiar": "NPE. Check for null before method calls, use Optional, verify object initialization, review stack trace for null source."
        },
        "java class not found": {
            "pattern": "ClassNotFoundException|NoClassDefFoundError|Could not find or load main class",
            "beginner": "Java can't find the class (code) it needs. This usually means a missing library or the classpath isn't set up correctly.",
            "familiar": "Missing class in classpath. Check dependencies, verify classpath (-cp), ensure correct package/class name."
        },
        "c compilation error": {
            "pattern": "undefined reference|multiple definition|implicit declaration|incompatible pointer type",
            "beginner": "The C/C++ compiler found an error in your code. 'Undefined reference' means a function is used but not defined. Check your linking and includes.",
            "familiar": "Linker/compiler error. undefined reference: add -l flag or link object file. implicit declaration: add #include. Check types for pointer issues."
        },
        "docker build cache": {
            "pattern": "COPY failed|ADD failed|no such file or directory.*docker",
            "beginner": "Docker can't find a file during the build process. Make sure the file exists and the path is correct relative to the Dockerfile location.",
            "familiar": "Docker build context issue. Check .dockerignore, verify file paths relative to build context, ensure files are committed."
        },
        "terraform state": {
            "pattern": "Error locking state|state lock|terraform.*state.*error",
            "beginner": "Terraform's state file is locked, usually because another operation is running or a previous one crashed. If no one else is using it, you may need to manually unlock.",
            "familiar": "State lock conflict. terraform force-unlock if safe, check for running operations, verify backend configuration."
        },
        "ansible connection": {
            "pattern": "UNREACHABLE|Failed to connect to the host|ansible.*connection.*refused",
            "beginner": "Ansible can't connect to the remote server. Check that SSH is working, the server is reachable, and you have the right credentials.",
            "familiar": "Ansible connection failure. Verify SSH access, check ansible_host/ansible_user, review inventory, test with ansible -m ping."
        }
    },
    "output_patterns": {
        "exit_code_0": {
            "pattern": "exit code 0|exited with 0|return code 0",
            "beginner": "Exit code 0 means SUCCESS! The program finished running without any errors. In the terminal world, 0 always means 'everything went well.'",
            "familiar": "Process exited successfully (return code 0)."
        },
        "exit_code_nonzero": {
            "pattern": "exit code [1-9]|exited with [1-9]|return code [1-9]",
            "beginner": "A non-zero exit code means something went wrong. The specific number can give hints about what failed, but you'll usually need to look at the error messages above this line for details.",
            "familiar": "Non-zero exit code indicates failure. Check stderr output for details. Common: 1 (general error), 2 (misuse), 126 (not executable), 127 (not found), 130 (Ctrl+C)."
        },
        "deprecation_warning": {
            "pattern": "DeprecationWarning|deprecated|will be removed",
            "beginner": "This is a warning (not an error) telling you that something you're using will stop working in a future version. Your code still works for now, but you should plan to update it to use the newer replacement.",
            "familiar": "Deprecation notice. Feature still works but will be removed in a future version. Update to recommended alternative when convenient."
        },
        "compilation_success": {
            "pattern": "compiled successfully|Build complete|webpack.*compiled|Successfully compiled",
            "beginner": "Your code was successfully compiled (translated into a form the computer can run). Everything is working and ready to go!",
            "familiar": "Build/compilation succeeded. Application is ready to run."
        },
        "server_started": {
            "pattern": "listening on|server.*started|running on.*port|started.*http",
            "beginner": "Your web server is now running! You can open your web browser and go to the address shown (usually something like http://localhost:3000) to see your application.",
            "familiar": "Server is up and listening. Navigate to the displayed URL to access the application."
        },
        "test_results": {
            "pattern": "\\d+ passed|\\d+ failed|Tests?:.*\\d|test.*suite|PASS|FAIL",
            "beginner": "These are the results of running your automated tests \u2014 little checks that verify your code works correctly. 'Passed' means the check worked, 'Failed' means something didn't work as expected.",
            "familiar": "Test execution results. Review failed tests, check assertions and expected vs actual values."
        }
    }
}


def load_knowledge_base(path=None):
    kb_path = path or DEFAULT_KB_PATH
    if os.path.exists(kb_path):
        try:
            with open(kb_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_KNOWLEDGE_BASE.copy()
    return DEFAULT_KNOWLEDGE_BASE.copy()


def save_knowledge_base(kb, path=None):
    kb_path = path or DEFAULT_KB_PATH
    try:
        with open(kb_path, "w") as f:
            json.dump(kb, f, indent=2)
        return True
    except IOError:
        return False


def validate_regex(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def ensure_knowledge_base_exists(path=None):
    kb_path = path or DEFAULT_KB_PATH
    kb_dir = os.path.dirname(kb_path)
    if kb_dir and not os.path.exists(kb_dir):
        os.makedirs(kb_dir, exist_ok=True)
    if not os.path.exists(kb_path):
        save_knowledge_base(DEFAULT_KNOWLEDGE_BASE, kb_path)
        return load_knowledge_base(kb_path)
    kb = load_knowledge_base(kb_path)
    if _merge_kb(kb, DEFAULT_KNOWLEDGE_BASE):
        save_knowledge_base(kb, kb_path)
    return kb


def lookup_command(text, kb, mode="beginner"):
    text_stripped = text.strip().lower()
    for cmd, explanations in kb.get("commands", {}).items():
        if text_stripped == cmd or text_stripped.startswith(cmd + " "):
            return explanations.get(mode, explanations.get("beginner", ""))
    first_word = text_stripped.split()[0] if text_stripped.split() else ""
    for cmd, explanations in kb.get("commands", {}).items():
        if first_word == cmd.split()[0]:
            return explanations.get(mode, explanations.get("beginner", ""))
    return None


def _merge_kb(existing, defaults):
    changed = False
    for section in ["commands", "error_patterns", "output_patterns"]:
        if section not in defaults:
            continue
        if section not in existing:
            existing[section] = {}
        for key, value in defaults[section].items():
            if key not in existing[section]:
                existing[section][key] = value
                changed = True
    return changed


def _safe_regex_search(pattern, text):
    try:
        return re.search(pattern, text, re.IGNORECASE) is not None
    except re.error:
        return False


def lookup_error(text, kb, mode="beginner"):
    for _name, error_info in kb.get("error_patterns", {}).items():
        pattern = error_info.get("pattern", "")
        if pattern and _safe_regex_search(pattern, text):
            return error_info.get(mode, error_info.get("beginner", ""))
    return None


def lookup_output(text, kb, mode="beginner"):
    for _name, output_info in kb.get("output_patterns", {}).items():
        pattern = output_info.get("pattern", "")
        if pattern and _safe_regex_search(pattern, text):
            return output_info.get(mode, output_info.get("beginner", ""))
    return None


def local_lookup(text, kb, mode="beginner"):
    result = lookup_error(text, kb, mode)
    if result:
        return {"source": "local_db", "category": "error", "explanation": result}

    result = lookup_output(text, kb, mode)
    if result:
        return {"source": "local_db", "category": "output", "explanation": result}

    result = lookup_command(text, kb, mode)
    if result:
        return {"source": "local_db", "category": "command", "explanation": result}

    return None
