# Installation

## Development Requirements

* python 3.0+
* opencv 3.1+

## Install Opencv (ubuntu 16.04)

source : [pyimagesearch](http://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/)

### required packages 

* build-essential 
* cmake 
* pkg-config

* libjpeg8-dev 
* libtiff5-dev 
* libjasper-dev 
* libpng12-dev

* libavcodec-dev 
* libavformat-dev 
* libswscale-dev 
* libv4l-dev

* libxvidcore-dev 
* libx264-dev

* libgtk-3-dev
* libatlas-base-dev 
* gfortran

* python2.7-dev 
* python3.5-dev

```bash
    sudo apt-get install \ 
    build-essential cmake pkg-config \
    libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev \
    libgtk-3-dev libatlas-base-dev gfortran \
    python2.7-dev python3.5-dev
```

### download source files

opencv 3.1 :
```
    wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip
    unzip opencv.zip
```

opencv contrib 3.1 :
```
    wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.1.0.zip
    unzip opencv_contrib.zip
```

### prepare python 

```
    pip install numpy
    pip3 install numpy
```

### Make and install

configure make :
```
    cd ~/opencv-3.1.0/
    mkdir build
    cd build
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
        -D CMAKE_INSTALL_PREFIX=/usr/local \
        -D INSTALL_PYTHON_EXAMPLES=ON \
        -D INSTALL_C_EXAMPLES=OFF \
        -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.1.0/modules \
        -D BUILD_EXAMPLES=ON ..
```

run make : 
```
    make -j4
```

install opencv: 
```
    sudo make install
    sudo ldconfig
```
