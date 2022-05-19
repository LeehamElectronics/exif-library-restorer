# exif-library-restorer
### 🌅 overview
an overly complicated couple of python scripts that fix one problem. One day I decided to copy my entire photo library over from a HDD Samba share to a new SSD Samba share. The files originated from a Windows machine, and some-where along the way, all of the photos had their 'date modified' metadata RESET to whatever the 'date created' metadata was, which of course was set to the time of the copy operation. In other words, most of my photos lost their time stamps. I didn't realise this had happened until much later on, after I had already spent MANY hours organising, renaming, deleting and adding to my new library on my SSD. It was too time-consuming to individually fix each file, so instead I made this tool that would take a hash value of every single file from the original and new library, and save that data with it's 'date-modified' data. Then the script will go through your new libraries files and rewrite it's date modified field to match the original libraries. In the process I also made it spit out some statistics about the libraries such as duplicate files and such. 

### 🤖 other info
youtube video in the making for anyone who needs additional help seeing how it works.

### 💻 how to use
if you're on linux, copy this repo into your home directory somewhere:
```
git clone https://github.com/LeehamElectronics/exif-library-restorer.git
```
cd into folder
```
cd exif-library-restorer
```
rename and chmod the scripts so you can run them on your pc
```
mv read_library.py read_library.sh; chmod +x read_library.sh
mv restore_library.py restore_library.sh; chmod +x restore_library.sh
```
run the read_library.sh script and follow the prompts for each of your libraries (original / new)
```
./read_library.sh
```
run the restore_library.py.sh script and follow the prompts
```
./restore_library.py.sh
```

Have any troubles or questions? Send me a message on my [Discord server](https://discord.gg/SM48CZhHbB)


