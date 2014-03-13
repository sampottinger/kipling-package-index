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
 - Get an account with KPI ```kpicmd.py login --new_user```
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

<br>
Info about KPI and how to contribute
------------------------------------
Released under [GNU GPL v3](https://www.gnu.org/copyleft/gpl.html). Patches and contributions welcome! Active maintainers:

 - [Sam Pottinger](https://github.com/samnsparky)
 - [Chris Johnson](https://github.com/chrisJohn404)
