Udacity FSDN course Catalog-app project.
#Installation

    Install Vagrant and VirtualBox
    Clone the fullstack-nanodegree-vm
    Launch the Vagrant VM (vagrant up)
    Write your Flask application locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM).
##Create a database `python /vagrant/catalog/database_setup.py`
    Insert a data records to the database  `python /vagrant/catalog/create_db_entries.py`
##Run your application within the VM `python /vagrant/catalog/project.py`
    Access and test your application by visiting http://localhost:5000 locally
