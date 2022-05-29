import sys
from pip.req import parse_requirements
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
#build_exe_options = {"packages": ["os"], "includes": ["tkinter"]}
install_reqs = [
    "affine==2.3.0",
    "asgiref==3.3.4",
    "attrs==21.2.0",
    "certifi==2021.5.30",
    "click==7.1.2",
    "click-plugins==1.1.1",
    "cligj==0.7.2",
    "cycler==0.10.0",
    "DateTime==4.3",
    "Django==3.2.3",
    "greenlet==1.1.0",
    "image==1.5.33",
    "kiwisolver==1.3.1",
    "matplotlib==3.4.2",
    "numpy==1.20.3",
    "opencv-python==4.5.2.52",
    "Pillow==8.2.0",
    "pyparsing==2.4.7",
    "pyproj==3.1.0",
    "pyshp==2.1.3",
    "python-dateutil==2.8.1",
    "pytz==2021.1",
    "scipy==1.6.3",
    "Shapely==1.7.1",
    "six==1.16.0",
    "snuggs==1.4.7",
    "SQLAlchemy==1.4.17",
    "sqlparse==0.4.1",
    "utm==0.7.0",
    "wheel==0.37.1",
    "zope.interface==5.4.0",
]
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="Meu App",
    version="0.1",
    description="Minha 1° Aplicação!",
    options={"build_exe": reqs},
    executables=[Executable("main.py")]
)