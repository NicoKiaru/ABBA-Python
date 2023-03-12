# MAKING AN INSTALLER

This folder contains some files which can be used to create an installer for ABBA by using https://github.com/conda/constructor

The yaml file contains the dependencies required to make the installer, but that's not all. Each OS has it own requirements.

Normally you won't need to use the content of this folder. It's just there for the main dev (Nico) that has to make releases from times to time. But if you're sufficiently knowledgable in python, you won't need the installer and will just run ABBA from source and by using the env yaml file in the parent directory.

## All OS

This folder:

- needs to contains an up-to-date `Fiji.app` folder, but without Java (take it from https://imagej.net/software/fiji/downloads, choose no JRE)
- then, in this Fiji, put ABBA, for instance by installing it from intellij and specifying the Fiji directory and maven build it.


## Windows

The win folder should also contain the elastix executable. Version 5.0.1: `win\elastix-5.0.1-win64`

Then run `prepare_win.bat` which copies the abba-python code in the same folder (that's because I do not know how to tar properly from another folder) and zips everything into a abba-pack-win.tar.gz file which will be included in the installer.

Then create a conda env, install conda constructor in it, and run `constructor .` once your current directory is there. After a few minutes, an executable file should be created. That's the installer!

It is big because it contains a pretty big conda environment, some models, java, and an almost complete Fiji.

## Mac

see https://github.com/NicoKiaru/ABBA-Python/issues/16

## Linux

see https://github.com/NicoKiaru/ABBA-Python/issues/17