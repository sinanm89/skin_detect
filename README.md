![Skinny logo](./skinny.jpg)

# Skinny : A Twisted JsonRPC Server Plugin for skin detection

This library will attempt to detect skin and nudity via links given in json remote procedure calls.

* Supports concurrent requests
* The skin and nudity detection are not %100 accurate
* See requirements.txt for instaled pip modules

---

[![Build Status](https://travis-ci.org/travis-ci/travis-build.png?branch=master)](https://magnum.travis-ci.com/ScrunchEnterprises/skinny.svg?token=QvWopK7QRTWF9JRypz9q&branch=master)
[![Coverage Status](https://coveralls.io/repos/ScrunchEnterprises/skinny/badge.svg?branch=master&service=github&t=5Vj96p)](https://coveralls.io/github/ScrunchEnterprises/skinny?branch=master)

---

Installation
============

The module assumes you will be working in a virtual environment however it should still work even if you dont.

MAC OSX
-------

Make sure Xcode is updated and make sure you've accepted the licence agreements by opening the Xcode.app after its installed.

Clone repo, setup and activate virtualenv:

```bash
$ git clone git@github.com:ScrunchEnterprises/skinny.git
$ cd skinny
$ sudo easy_install pip
$ pip install virtualenv
$ virtualenv env
$ source env/bin/activate
```
**From now on its assumed you're in your virtualenv and in the current project folder unless stated otherwise.**

Install required pip packages in `requirements.txt`.

```
$ pip install -r requirements.txt
```

**The following is for installing opencv 3.0.0 under virtualenv if you'd like a global opencv interpreter you can skip the next part to [Usage](#usage)**

```
$ wget https://github.com/Itseez/opencv/archive/3.0.0.zip
$ unzip -a 3.0.0.zip
```

or manually download opencv-3.0.0 from [here](https://github.com/Itseez/opencv/archive/3.0.0.zip) or go to [their site](http://opencv.org/downloads.html) and build the binaries for the virtualenv

```
$ cd opencv-3.0.0
$ mkdir release
$ cd release
$ cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV \
-D PYTHON2_PACKAGES_PATH=$VIRTUAL_ENV/lib/python2.7/site-packages \
-D PYTHON2_LIBRARY=$VIRTUAL_ENV/bin \
-D PYTHON2_INCLUDE_DIR=$VIRTUAL_ENV/include/python2.7 \
-D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=OFF \
-D BUILD_EXAMPLES=OFF \
-D OPENCV_EXTRA_MODULES_PATH=$VIRTUAL_ENV/opencv_contrib/modules ..
```
The following command will take a while to make.
```
$ make -j4
$ make install
```

After its done run the tests to see if it works

---

Optionally it can append your PYTHONPATH to the skinny project directory or append the following line to your activate script.

```
echo "\nexport PYTHONPATH=$(pwd)" >> $VIRTUAL_ENV/bin/activate
```

---

```
$ trial skinny
```

# Usage

While your virtual environment is active simply type:

```
$ twistd skinny
```
or

```
$ twistd -n skinny
```
for a non-daemonized process.


<!-- Contributing -->
<!-- ------------ -->

<!-- See [Contributing](CONTRIBUTING.md) -->