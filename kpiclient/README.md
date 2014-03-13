Kipling Package Index command line tool
=======================================

Kipling Package Index command line tool that allows for basic management of user
accounts as well as create, read, update, and delete (CRUD) control over the
package index.

<br>
Install
-------
 - Get Python and Pip! [Mac](http://docs.python-guide.org/en/latest/starting/install/osx/), [Linux](http://docs.python-guide.org/en/latest/starting/install/linux/), [Windows](http://docs.python-guide.org/en/latest/starting/install/win/)
 - Get KPI with ```pip install kpicmd```
 - Get an account with KPI ```kpicmd.py useradd [username]```
 - Check your email and update your password ```kpicmd.py passwd [username]```

<br>
Usage
-----
**Create a packa**  
Usage: ```kpicmd.py create [module] [path to module.json]  [path to zip]```  
Example: ```kpicmd.py create simple_ain ./module.json ./simple_ain_001.zip```

**Read current information about a packa**  
Usage: ```kpicmd.py read [name of module]```  
Example: ```kpicmd.py read simple_ain```

**Update a packa**  
Usage: ```kpicmd.py update [module] [path to module.json] [path to zip]```  
Example: ```kpicmd.py update simple_ain ./module.json ./simple_ain_001.zip```

**Delete a package**  
Usage: ```kpicmd.py delete [name of module]```  
Example: ```kpicmd.py delete simple_ain```

**Register a new username with K**  
Usage: ```kpicmd.py useradd [username]```  
Example: ```kpicmd.py useradd samnsparky```

**Update user password for KPI**  
Usage: ```kpicmd.py passwd [username]```  
Example: ```kpicmd.py passwd samnsparky```

<br>
Automated Tests
---------------
Want to test kpiclient itself? ```python kpiclient_test.py```

<br>
Contribute and more info
------------------------
Patches and issues are welcome! Active maintainer is [Sam Pottinger](https://github.com/Samnsparky) under the [GNU GPL v3](https://www.gnu.org/copyleft/gpl.html). See our [Git repo](https://github.com/Samnsparky/kipling-package-index) for more information!
