These instructions were written for Ubuntu-based distributions. Appropriate changes may need to be made for other flavors.
Assuming that Apache is installed correctly, the most valuable logs for troubleshooting will be /var/log/apache2/error.log and /var/log/apache2/access.log.

## Installation
Let's first install everything we're going to need for Apache:
	`sudo apt-get install apache2 apache2-utils libexpat1 ssl-cert python`

- ensure you have Apache installed and running with `sudo service apache2 status`


Then let's grab the WSGI module that allows Apache to play nicely with Python applications:
	- download the source tarball from https://pypi.python.org/packages/15/d4/83c842c725cb2409e48e2999e80358bc1dee644dabd1f3950a8dd9c5a657/mod_wsgi-4.5.24.tar.gz
	- unpack the .tar.gz with `tar xvzf mod_wsgi-4.5.24.tar.gz`
	- configure and install the module with the following:
		`sudo ./configure --with-python=[location of Python3.x installation]`
		`sudo make`
		`sudo make install`
		
## Virtual Environment		
Now we're ready to make an application and configure Apache. First let's take care of virtual environments.
- create a virtual environment for this project, specifically:
	`python3 -m venv [path of virtual env]`

- test that this installation worked correctly by activating this virtual environment:
	`. [full path to virtual env]/bin/activate`

Now you're using the virtual environment for this application. Any package dependencies that your application has should be installed here using `pip install`.

For Apache to play nicely with WSGI in an environment containing multiple Python installations, we need an 'empty' virtual environment to act as the 'main installation of Python' as far as Apache is concerned.
- create this virtual env:
	`python3 -m venv [path of virtual env]`
			
## Application			
Next we can make the Flask application that Apache will run. First, let's activate the application's virtual environment and install Flask:
	`. [path to virtual env]/bin/activate`
	`pip install Flask`
		
Now, create a file [application].py in the location that you would like the source of your project to be. Here is a simple "Hello World" that returns JSON data:
```
	from flask import Flask, Response
	import json

	app = Flask(__name__)


	@app.route("/")
	def hello():
		return Response(json.dumps({"hello": "world"}))


	if __name__ == "__main__":
		app.run(debug=True)
```

## WSGI Configuration			
Then, let's create our .wsgi config file, which will be responsible for translating our Flask API and gathering necessary environment variables. Create a directory for your project, /var/www/[project], and add this to [project].wsgi in that directory:
```
	import sys
	import site

	sys.path.append('[full path to Flask application]')

	python_version = '.'.join(map(str, sys.version_info[:2]))
	python_home = '[full path to the application virtual env]'

	site_packages = python_home + '/lib/python%s/site-packages' % python_version

	site.addsitedir(site_packages)

	from [name of Flask application] import app as application
```
		
## Apache Configuration			
Add this to /etc/apache2/conf-available/wsgi.conf:
```
	WSGIDaemonProcess [name for process] user=[non-root user for process] group=[non-root group for process] processes=[# of parent processes] threads=[# of threads per parent] home=[directory containing .wsgi conf file] python-home=[empty virtual env]
	WSGIScriptAlias /[url path to access app] [full path to .wsgi conf file]

	<Directory [directory containing .wsgi conf file; above]>
		WSGIProcessGroup [name for process; above]
		WSGIApplicationGroup %{GLOBAL}
		Require all granted
	</Directory>
```
	
Finally, restart Apache and see if the changes took. For now, you'll be able to access the app at localhost/[url path to access app; above].
	
If you'd like to access the app elsewhere, at 'go/[url path to access app; above] for example, simply add the following line to /etc/hosts:
	`127.0.0.1 go`
