## Installation instructions:
----
> Before doing any of this, download the latest image of OSMC and flash it to an SD-card. 

### Update apt

```
sudo apt update
```

### osmc recommended way, instead of `apt upgrade`

```
sudo apt dist-upgrade
```

### Watch some netflix

### Required to install berryconda later on
```
$ sudo apt install bzip2
```

### Autoconf required by hass
```
$ sudo apt-get install autoconf
```

### Add a new user
```
$ sudo useradd -rm homeassistant
```

### Create a homeassistant directory in /srv
```
$ cd /srv/
$ sudo mkdir homeassistant
```

### Give the homeassistant user ownership of this directory
```
$ sudo chown homeassistant:homeassistant homeassistant
```

### Switch to the new `homeassistant` user
```
$ sudo su -s /bin/bash homeassistant
```

### Download berryconda3 and install
```
$ wget https://github.com/jjhelmus/berryconda/r eleases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv7l.sh
$ chmod +x Berryconda3-2.0.0-Linux-armv7l.sh
$ ./Berryconda3-2.0.0-Linux-armv7l.sh
```

### Optional but needed for my
```
$ sudo apt-get install build-essential
```

### Make sure you are where we want to launch hass from
```
$ cd /srv/homeassistant
```

### Install Cython using conda, so we don't need to compile it on the rpi
```
$ conda install cython
```

### Make sure you are using the correct pip version (e.g /home/homeassistant/berryconda3/bin/pip) 
```
$ whereis pip
```

### Install and run hass
```
$ pip install homeassistant 
$ hass
```

Now, let it finish, and test the server at <http://YOUR_IP:8213> and see that everything is working (this might take a while). If all good, move on to installing the daemon to add it to auto start

Note: If you want to run it in a virtual environment, and it gives you this error

```
python -m venv .
Error: Command '['/home/homeassistant/lol/bin/python', '-Im', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1
```

just do it like this
```
python3.6 -m venv --without-pip myvenvdir
source myvenvdir/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
deactivate
source myvenvdir/bin/activate
```

Now packages install with `pip install` will be local to the virtual environment