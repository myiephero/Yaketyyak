import json
import os
import re

DEFAULT_KB_PATH = "terminal_knowledge_base.json"

DEFAULT_KNOWLEDGE_BASE = {
    "commands": {
        "ls": {
            "beginner": "This command lists all the files and folders in your current directory (like opening a folder on your desktop to see what's inside).",
            "familiar": "Lists directory contents. Common flags: -l (long format), -a (show hidden), -h (human-readable sizes)."
        },
        "cd": {
            "beginner": "This command changes which folder you're currently working in. Think of it like double-clicking a folder to go inside it. 'cd ..' goes back up one level.",
            "familiar": "Change directory. Use 'cd ..' to go up, 'cd ~' for home, 'cd -' for previous directory."
        },
        "pwd": {
            "beginner": "This shows you the full path of the folder you're currently in. It's like looking at the address bar in a file explorer to see where you are.",
            "familiar": "Print working directory \u2014 shows the absolute path of your current location."
        },
        "mkdir": {
            "beginner": "This creates a new folder. For example, 'mkdir my_project' makes a new folder called 'my_project'.",
            "familiar": "Create a new directory. Use -p to create nested directories (e.g., mkdir -p a/b/c)."
        },
        "rm": {
            "beginner": "This deletes a file permanently (it does NOT go to the trash). Be very careful with this! 'rm -r' deletes entire folders and everything inside them.",
            "familiar": "Remove files/directories. -r for recursive, -f for force (no confirmation). Use with caution."
        },
        "cp": {
            "beginner": "This copies a file from one place to another. For example, 'cp file.txt backup.txt' makes a copy of file.txt called backup.txt.",
            "familiar": "Copy files/directories. Use -r for directories, -i for interactive (confirm overwrite)."
        },
        "mv": {
            "beginner": "This moves a file to a different location OR renames it. 'mv old_name.txt new_name.txt' renames the file.",
            "familiar": "Move or rename files/directories. Also used for renaming in-place."
        },
        "cat": {
            "beginner": "This displays the entire contents of a file right in your terminal, like opening a text file to read it.",
            "familiar": "Concatenate and display file contents. For large files, consider using 'less' or 'head'/'tail' instead."
        },
        "grep": {
            "beginner": "This searches through files to find lines that contain specific text. It's like using Ctrl+F (Find) but for files in your terminal.",
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
        "npm install": {
            "beginner": "This downloads and installs a JavaScript/Node.js package so you can use it in your project. It saves it in a folder called 'node_modules'.",
            "familiar": "Install Node.js packages. --save-dev for dev dependencies, -g for global install."
        },
        "git clone": {
            "beginner": "This downloads a complete copy of a project from the internet (usually from GitHub) to your computer so you can work on it.",
            "familiar": "Clone a remote repository. Use --depth 1 for shallow clone, --branch to specify branch."
        },
        "git add": {
            "beginner": "This tells Git to start tracking changes you've made to specific files. It's like putting files in a 'ready to save' staging area.",
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
            "beginner": "This shows you which files have been changed, which are staged (ready to commit), and which are not being tracked by Git.",
            "familiar": "Show working tree status. -s for short format, --branch for branch info."
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
            "beginner": "This prints text to the terminal. It's often used in scripts to show messages or to write text into files.",
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
        "top": {
            "beginner": "This shows you a live updating list of all running programs and how much of your computer's resources (CPU, memory) they're using.",
            "familiar": "Real-time process monitor. Press 'q' to quit, 'M' to sort by memory, 'P' by CPU. Consider using htop."
        },
        "man": {
            "beginner": "This opens the manual (help documentation) for any command. For example, 'man ls' shows you everything you can do with the 'ls' command.",
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
    if not os.path.exists(kb_path):
        save_knowledge_base(DEFAULT_KNOWLEDGE_BASE, kb_path)
    return load_knowledge_base(kb_path)


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
