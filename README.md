# References Manager
Web-Based application to organize and display pictures create by and for digital artist


![references-manager](static/docs/screen_01.png)


Features
--------

- Display pictures
- Searching functionality by Artist name, Tags and Color
- Automatic detection of color when you import a picture
- Link to other application ([Krita](https://krita.org/en/), [PureRef](https://www.pureref.com/), etc..) 

Dependencies
------------

### Python 

|        | Version |
| ------ | ------- |
| Python | \>= 3.6 |

### Packages :

| Python Packages      | Version     |
| -------------------- | ----------- |
| pyqt5                | \>= 5.14.5  |
| PyQtWebEngine        | \>= 5.14.5  |
| Flask                | \>= 1.1.2   |
| pillow               | \>= 7.0.0   |
| requests             | \>= 2.22.0  |
| bs4                  | \>= 0.0.1   |

Installation
------------

1. Install [python](https://www.python.org/) version superior or equal to 3.6
2. Clone this repository or download the zip file and extract
   ```
    > git clone https://github.com/fabiencollet/references-manager.git
   ```
3. In a terminal navigate to the folder of the application like :
   - Windows :
   ```
    > cd C:\Users\<username>\Documents\references-manager
   ```
   - OSX :
    ```
    > cd /Users/<username>/references-manager
   ```
   - Linux :
   ```
    > cd /home/<username>/references-manager
   ```
4. Install python dependencies with the command
   ```
    > pip install .
   ```
   or
   ```
    > pip3 install .
   ```
5. It's Done !!

Launch App
----------

### Desktop Browser
1. Open the file app.py

### Web Browser

#### Windows

1. launch run_server_win.bat
2. launch file open_win.bat

#### OSX

1. launch run_server_osx.sh
2. launch open_osx.sh

#### Linux

1. launch run_server_linux.sh
2. launch open_linux.sh
