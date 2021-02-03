# Pypi-uploader
#### Upload your Python libraries to PyPi with a beautiful interface.

</br>

<a href="README_RU.md" ><img src="https://emojio.ru/images/twitter-64/1f1f7-1f1fa.png" width="30" height="30"></img>Читать на Русском</a>
</br></br>

This program is written using the <a href="https://pypi.org/project/PySimpleGUI/">PySimpleGUI</a> library.

Just run <a href="Pypi_uploader.py">Pypi_uploader.py</a> and follow the instructions on the screen.</br>
The program will automatically install the necessary libraries, compile your project into an archive and upload it to Pypi or Test Pypi.</br>
After uploading, program can also clean up all generated files.

#### Important! Selected project folder should contain the ```__init__.py``` file! This is the main file of your library.

#### Folder hierarchy:
```
.../Any_folder_name
     |__Pypi-uploader.py
     |__Your_Project_Folder/
         |__ __init__.py
         |__Other_files... 
```

<img src="Image.png"></img>

#### If you are using api key

Username: ```__token__``` </br>
Password: *The token value, including the ```pypi-``` prefix*
