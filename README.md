Kipling Package Index
======================================
LabJack's package manager, keeping LabJack software utilities up to date across platforms and software distribution. Part of the Kipling Web Services (KWS) suite for the greater good.

<br>
Motivation
----------
 - Hardware bound cross platform application development sucks. It sucks less with Kipling.
 - Distributing cross platform applications and keeping them up to date sucks. It sucks less with KPI.
 - Life is too short. Test, deploy, and go home for the day.

<br>
Installation
------------
 - Get Python and Pip! [Mac](http://docs.python-guide.org/en/latest/starting/install/osx/), [Linux](http://docs.python-guide.org/en/latest/starting/install/linux/), [Windows](http://docs.python-guide.org/en/latest/starting/install/win/)
 - Get KPI with ```pip install kpicmd```
 - Get an account with KPI ```kpicmd.py useradd [username]```
 - Check your email and update your password ```kpicmd.py passwd [username]```

<br>
Usage
-----
**Create a package**  
Usage: ```kpicmd.py create [name of module] [path to module.json]  [path to zip archive]```  
Example: ```kpicmd.py create simple_ain ./module.json ./simple_ain_001.zip```

**Read current information about a package**  
Usage: ```kpicmd.py read [name of module]```  
Example: ```kpicmd.py read simple_ain```

**Update a package**  
Usage: ```kpicmd.py update [name of module] [path to module.json] [path to zip archive]```  
Example: ```kpicmd.py update simple_ain ./module.json ./simple_ain_001.zip```

**Delete a package**  
Usage: ```kpicmd.py delete [name of module]```  
Example: ```kpicmd.py delete simple_ain```

**Register a new username with KPI**  
Usage: ```kpicmd.py useradd [username]```  
Example: ```kpicmd.py useradd samnsparky```

**Update user password for KPI**  
Usage: ```kpicmd.py passwd [username]```  
Example: ```kpicmd.py passwd samnsparky```

<br>
Extra fields for module.json
----------------------------
There are some extra fields that KPI looks for in your module.json file...

**authors**  
Usage: ```"authors": [usernames authorized to modify this entry]```  
Example: ```"authors": ["samnsparky", "chrisJohn404"]```  
Required: ```Yes```

**license**  
Usage: ```"license": "Name of license your module is released under"```  
Example: ```"license": "GNU GPL v3"```  
Required: ```Yes, but defaults to GNU GPL v3 if not provided```

**description**  
Usage: ```"description": "Short markdown description of your module"```  
Example: ```"description": "GUI for [analog inputs](labjack.com/support/faq/what-is-analog-input)."```  
Required: ```No, but strongly encouraged```

**homepage**  
Usage: ```"homepage": "URL for the homepage for this module"```  
Example: ```"homepage": "https://github.com/Samnsparky/kipling-package-index"```  
Required: ```No```

**repository**  
Usage: ```"repository": "URL to the repository for this module's code"```  
Example: ```"repository": "https://github.com/Samnsparky/kipling-package-index.git"```  
Required: ```No```


<br>
Info about KPI and how to contribute
------------------------------------
Released under [GNU GPL v3](https://www.gnu.org/copyleft/gpl.html). Patches and contributions welcome! Active maintainers:

 - [Sam Pottinger](https://github.com/samnsparky)
 - [Chris Johnson](https://github.com/chrisJohn404)
