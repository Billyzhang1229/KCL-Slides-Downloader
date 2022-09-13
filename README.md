# KCL Slides Downloader
This is a simple downloader to help you download kcl course slides

## Usage

1. install required packages
```
pip install -r requirements.txt
```
2. run the script
```
python main.py
```
3. Go to Keats, copy the url of the course page and paste it in the the script and press enter
```
1. Open the browser and go to Keats
2. Click on the course you want to download
3. Copy the url of the course page
```
4. You will need cookies to download the slides (you can use the cookies from your browser)
```
For Chrome
1. Press F12 or right click on the browser  and select "Inspect" to open the developer tools
2. Click on the "Network" tab (if nothing is shown, refresh the page)
3. Choose the one called "view.php?id=xxxxx"
4. Copy the cookies from the "Headers" tab
```
5. Paste the cookies in the script and press enter
6. Choose wether you to download all the slides in one folder or by week and press enter
7. Done!

Not garenteed to work with all courses, but it should work with most of them.
