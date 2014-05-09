WatcherApp
==========

This is assignment for job interview.
Assignment was to build minimalistic 'image bank' application with with limited search capabilities including background processing.

What was done:
* The system should monitor one folder on the local file system (watch-folder) and register any newly appearing files to the database as a background process without any manual involvement.
* It should be possible to perform substring search for file names registered.
* It should be possible to assign "metadata" to any file through the user-interface
* It should be possible to search for metadata
* It should be possible to delete registered files from the web-UI
* The System should have at least the following views:
  * File name search + presentation of search results
  * View a file with metadata in web-interface if available. Also display image on this page if it is an image
  * Edit metadata for a file

* Ability to have multiple metadata fields per file

What was used
=============
Application was written using:

* **Python** with **Flask** microframework
* **PostgreSQL** as main sql storage
* **Flask-SQLAlchemy** - flask extension for SQLAlchemy ORM
* **Sqlalchemy-Enum-Dict** - Enum column implementation for SQLAlchemy
* **Flask-Script** - extension for writing external scripts in Flask
* **requests** - library for making http requests
* **python-magic** - library used for getting Mimetype info from file
* **watchdog** - library for monitoring filesystem events

Also for system deploy/work was used:
* **Vagrant** - tool for building complete development environments
* **Ansible** - orchestration engine
* **Supervisor** - process control system
* **nginx** - http proxy server

Internals
---------
Inside we have 2 different applications managed by `supervisor`.
One for moninoring changes inside watched directory and making http post for every change to flask application.
And the second is actual flask application.
Separation of this services making its possible to scale to any size and to host any number of watchers on any number of hosts.

Requirements
============
* vagrant [http://www.vagrantup.com/downloads.html](http://www.vagrantup.com/downloads.html)
* virtualbox [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)
* ansible [http://docs.ansible.com/intro_installation.html](http://docs.ansible.com/intro_installation.html)
* python>=2.7

Installation
=============
All you need to run application is enter application directory and run

    # vagrant up

This will create new box with ubuntu 12.04 inside, then all needed packages
like postgresql, nginx, supervisor, etc. will be installed and configured.

Usage
=====

Web application should be accessible at `http://localhost:8080`
Application is configured to watch directory named `watch_here`.
After start system will monitor all file changes in this directory(excluding subdirectories).

Web has several views:
* *mainpage/recent* - by default when you access `/` you will see 20 most recently updated files.
    From this view you can view/edit each of files by clicking on its filename or you can delete file.
* *deleted* - list of deleted files. From this list you can also view file, and recover it(i.e. remove `deleted` mark)
* *settings* - list of all metadata fields with their descriptions. Here you can create new fields.
* *item_view* - page with all info about the file with metadata attached. If its an image also preview will be shown.
  From this view you can add/remove/edit metadata for this file.
* *search* - search box is visible on every page and has two scope options, search in filenames or in metadata values.
  Search results will be shown the same way as files in recent/deleted views.

Renaming:
---------
Rename of file works as delete one file and add new one. So metadata will be not saved during renaming.

Deleting:
---------
You can delete files in 2 different ways.
* First is to delete through the web. Deleting this way will mark file as deleted(File will be not listing anywhere except `deleted` list).
Physical file will not be deleted. You can undo this action anytime.
* Second way is to delete file from filesystem. If this will happen file will be also deleted from database with all its metadata. This can not be undone.

Search:
-------
Search is a sql `ilike` statement with preselected scope.
