# LSH-Plagiarism-Detector
The project aims to take one file (the `main.txt` file) and compares it to all the documents available in the `documents/` folder.

It will print out all the documents that are similar depending on the threshold you set manually.

You need to have `numpy` installed:

```sh
pip install numpy
```

There is even a `rename_files.py` that renames all your `.txt` files if you don't have them named correctly, execute it before running the `main.py` file.

# Update
I have added an UI Interface using `SwiftUI`, it’s MacOS only though, it has a modern drag&drop style to it and communicates with the python backend.

Feel free to fork the project ^^