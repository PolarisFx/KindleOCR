# KindleOCR

Forked Script of "raudette/kindleOCRer" to remove the DRM from a Kindle book - but rather than breaking the DRM, the book is captured, OCR'd, and an ePub is created.  Since forking I have been changing things to work with the current version of the required packages, and try to get an epub that better matches the novel given. With the original script any bolded text would be identified as a chapter heading. And left a very messed up epub. The current version has much better chapter detection. 

The script opens the selected book in the Kindle web reader with Chrome.  With the [Selenium](https://www.selenium.dev/) web automation tool, pages are flipped and screen captured.  The screen shots are saved to a PDF, an OCR process is run with [Marker](https://github.com/VikParuchuri/marker), and the output is saved as an ePub with [pypandoc](https://github.com/JessicaTegner/pypandoc).

## Requirements

- Python >= 3.10
- Chromium
- Has only been tested in Linux
- A Kindle account with the book to be converted

## Installation and Startup

Update .env with your settings, then install the requirements by running:
```
pip install -r requirements.txt

```

## Usage

Open the desired Kindle book on the Amazon web reader - it is [https://read.amazon.ca in Canada](https://read.amazon.ca) - with Chrome, and advance to the desired starting page.  I suggest advancing to the first reading page, past the Table of Contents.

Close Chromium.  Then run:

```
python KindleOCR.py --title="Kindle Book Title" --jobname="OCR job name"
```
If the Chrome profile selected by Selenium does not have your Amazon credentials, you will have 30 seconds to log in before the script times out.

The captured and converted Kindle book will be exported to ./output/jobname/jobname.epub

Note:
- The screen capture step will stop on the last page for about 30 seconds
- the first time the script is run, the Marker library has to download its OCR models.  
