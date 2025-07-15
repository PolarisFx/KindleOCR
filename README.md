# KindleOCR

Forked Script to remove the DRM from a Kindle book - but rather than breaking the DRM, the book is captured, OCR'd, and an ePub is created.  The output is not as nearly as good as the original format, but creating the script was a fun exercise, and perhaps it will prove to be useful to someone.  

The script opens the selected book in the Kindle web reader with Chrome.  With the [Selenium](https://www.selenium.dev/) web automation tool, pages are flipped and screen captured.  The screen shots are saved to a PDF, an OCR process is run with [Marker](https://github.com/VikParuchuri/marker), and the output is saved as an ePub with [pypandoc](https://github.com/JessicaTegner/pypandoc).

Inspired by the [Stripping Kindle DRM With Lego](https://hackaday.com/2013/09/09/stripping-kindle-drm-with-lego/) project which appeared in Hackaday.

## Requirements

- Python >= 3.10
- Chrome
- Has only been tested in Linux
- A Kindle account with the book to be converted

## Installation and Startup

Update sampledotenv with your settings and save as .env, then install the requirements by running:
```
pip install -r requirements.txt
```

## Usage

Open the desired Kindle book on the Amazon web reader - it is [https://read.amazon.ca in Canada](https://read.amazon.ca) - with Chrome, and advance to the desired starting page.  I suggest advancing to the first reading page, past the Table of Contents.

Close Chrome.  Then run:

```
python kindleOCRer.py --title="Kindle Book Title --jobname="OCR job name"
```
If the Chrome profile selected by Selenium does not have your Amazon credentials, you will have 30 seconds to log in before the script times out.

The captured and converted Kindle book will be exported to ./output/jobname/jobname.epub

Note:
- The screen capture step will stop on the last page for about 30 seconds
- the first time the script is run, the Marker library has to download its OCR models.  

## Screenshot

![Kindle Book and Exported ePub](/kindleOCRerscreenshot.png)
