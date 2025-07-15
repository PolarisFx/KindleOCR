from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from PIL import Image
import io
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
import pypandoc
import os
from dotenv import load_dotenv
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("--title", help="Name of the Kindle title to convert", type=str,required=True)
parser.add_argument("--jobname", help="Set a name for the conversion job", type=str,required=True)
args = parser.parse_args()

title=args.title
jobname = args.jobname
jobfolder = "./output/"+args.jobname+"/"

os.makedirs(jobfolder)

load_dotenv()

kindle_url=os.getenv("KINDLE_URL")
user_data_directory=os.getenv("USER_DATA_DIRECTORY")
profile_directory=os.getenv("PROFILE_DIRECTORY")
max_pages = int(os.getenv("MAX_PAGES"))
crop_header_px = int(os.getenv("CROP_HEADER_PX"))
crop_footer_px = int(os.getenv("CROP_FOOTER_PX"))

print("Capturing Screenshots of Each Page")
options = webdriver.ChromeOptions()
options.add_argument(r"--user-data-dir="+user_data_directory) #e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
options.add_argument(r'--profile-directory='+profile_directory) 
#driver = webdriver.Chrome()
driver = webdriver.Chrome(options=options)
driver.get(kindle_url)
driver.implicitly_wait(30) # I think this means wait for up to 10 seconds for a page to load when looking for something
driver.fullscreen_window()
#you can login here if you're not logged in
#we want to limit the list of titles to just the one we're looking for
elem = driver.find_element(By.ID, "search-bar")
elem.send_keys(title)
elem.send_keys(Keys.RETURN)
elem = driver.find_element(By.ID, "search-bar")

#now let's look for a cover image we can click on
elem = driver.find_element(By.XPATH, "//img[starts-with(@id, 'cover')]")
elem.click()
time.sleep(5)

#select single column mode
elem = driver.find_element(By.XPATH, "//*[@aria-label='Reader settings']")
elem.click()
time.sleep(2)
elem = driver.find_element(By.XPATH, "//*[@aria-label='Single Column']")
elem.click()
time.sleep(2)
elem = driver.find_element(By.CLASS_NAME, "side-menu-close-button")
elem.click()

#capturing process setup
time.sleep(2)
driver.fullscreen_window()
time.sleep(2)
elem = driver.find_element(By.CLASS_NAME, "pagination-container")
elem.click()
time.sleep(5)
endofbook = False
page = 0
book = []

#set the image dimensions to 
screenshot_for_size = driver.get_screenshot_as_png()
screenshot_for_size_as_io = io.BytesIO(screenshot_for_size)
screenshot_for_size_image = Image.open(screenshot_for_size_as_io)
height = screenshot_for_size_image.height
width = screenshot_for_size_image.width
box= (0, crop_header_px, width, height-crop_footer_px)

#page flipping.  assumes book is set to the start of what we want to capture
while not endofbook:
    screenshot = driver.get_screenshot_as_png()
    screenshot_as_io = io.BytesIO(screenshot)
    screenshot_image = Image.open(screenshot_as_io)
    screenshot_image_crop = screenshot_image.crop(box)
    #if we keep seeing the same page over and over again after right arrow, we're at the end of the book
    page_match_count=0
    book.append(screenshot_image_crop)
    try:
        elem=driver.find_element(By.ID, "kr-chevron-right")
        actions=ActionChains(driver)   
        actions.send_keys(Keys.RIGHT)
        actions.perform()
        time.sleep(.5)
        page=page+1    
    except:
        #the right arrow / kr-chevron right isn't on this page, we have reached end of book
        endofbook=True

    if page > max_pages:
        print("Capture has reached max_pages")
        endofbook=True
        
for idx, x in enumerate(book):
    book[idx].save(jobfolder+str(idx)+'.png')

driver.quit()

print("Creating PDF of screenshots")

book[0].save(
    jobfolder+jobname+".pdf", "PDF" ,resolution=100.0, save_all=True, append_images=book[1:]
)

print("Running OCR.  Converting PDF to Markdown")

converter = PdfConverter(
    artifact_dict=create_model_dict(),
)
rendered = converter(jobfolder+jobname+".pdf")
text, _, images = text_from_rendered(rendered)
print("done")

with open(jobfolder+jobname+".md", 'wt') as f:
    f.write(text)

for idx, x in enumerate(images):
    images[x].save(jobfolder+x)

input_markdown_file = jobfolder+jobname+".md"
output_epub_file = jobfolder+jobname+".epub"
temp_markdown_file = jobfolder+jobname+".temp.md" # A temporary file for the modified markdown

print("Running OCR.  Converting Markdown to ePub")

# Read the original Markdown content
with open(input_markdown_file, 'r', encoding='utf-8') as f:
    markdown_content = f.read()

# Replace '## ' with '**' at the beginning of a line and add closing '**'
# This regex looks for '## ' at the start of a line (^)
# and captures the rest of the line (.*)
# Then it replaces it with '**\1**' where \1 is the captured text.
processed_content = re.sub(r'^(##\s*)(.*)$', r'**\2**', markdown_content, flags=re.MULTILINE)

# Save the processed content to a temporary file
with open(temp_markdown_file, 'w', encoding='utf-8') as f:
    f.write(processed_content)

try:
    # Convert the temporary Markdown file to EPUB
    # Explicitly set --epub-chapter-level=1 to ensure only # (h1) creates chapters
    # Use --split-level=1 for Pandoc 3+
    pandoc_args = [f'--split-level=1 --resource-path='+jobfolder]
    pypandoc.convert_file(
        temp_markdown_file,
        'epub',
        outputfile=output_epub_file,
        extra_args=pandoc_args
    )
    print(f"Successfully converted '{input_markdown_file}' to '{output_epub_file}'")

except Exception as e:
    print(f"Error during Pandoc conversion: {e}")

finally:
    # Clean up the temporary file
    import os
    if os.path.exists(temp_markdown_file):
        os.remove(temp_markdown_file)
