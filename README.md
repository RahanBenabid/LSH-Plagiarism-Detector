# LSH-Plagiarism-Detector
The project aims to take one file (the `main.txt` file) and compares it to all the documents available in the `documents/` folder. The `main.txt` file should be placed in the root of the folder..

It will show all the documents that are similar depending on the threshold you set manually.

You need to have `numpy` installed:

```sh
# install dependency
pip install numpy
```

There is even a `rename_files.py` that renames all your `.txt` files if you don't have them named correctly, execute it before running the `main.py` file.

# GUI Update ✨
I have added an UI Interface using `SwiftUI`, it’s MacOS only though, it has a modern Drag & Drop style to it and communicates with the python backend made in flask.

![Screenshot](./images/Screenshot.png "Screenshot")

Before running it you need to have the server file running:

```sh
# install dependency
pip install flask

# start the server
python3 Python/server.py
```

Then open the project using *Xcode* and run it, it will do the same things as the backend, compare the file you dropped in the app to the files in the `/document` folder.

Feel free to fork the project ^^