#!/usr/bin/python
# -*- coding:utf-8 -*-

# Importing the required libraries
import csv, gspread, sys, os

from PIL import Image, ImageDraw, ImageFont
from oauth2client.service_account import ServiceAccountCredentials

base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
picdir = os.path.join(base_path, "pic")
libdir = os.path.join(base_path, "lib")
if os.path.exists(libdir):
    sys.path.append(libdir)
from waveshare_epd import epd7in5_V2

# Define global constants
WHITE = 255
GREY = 35
BLACK = 0
FONT = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), GREY)


# Encapsulate code into functions
def get_worksheet(sheet_name, i):
    # Set up OAuth2 credentials
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)

    # Authorize the client and open the spreadsheet
    client = gspread.authorize(creds)
    spreadsheet = client.open(sheet_name)

    # Return the target worksheet
    return spreadsheet.get_worksheet(i)


def write_to_e_paper(values):
    values = values[:15]  # Trim values to 15 lines max

    # e-Paper display stuff
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.Clear()

    # Set up the target Image
    image = Image.new("1", (epd.height, epd.width), WHITE)
    draw = ImageDraw.Draw(image)

    # Write new values to the Image
    print("rendering display")
    for i, value in enumerate(values):  # Use loops whenever possible
        # PEP8 says no spaces around ´=´ when using it for keyword arguments
        draw.text((2, 50 * i), value, font=FONT, fill=BLACK)

    # Send final image to the display
    epd.display(epd.getbuffer(image))
    epd.sleep()
    print("sleeping")


# Only run this code if script is directly called, not when being imported from
if __name__ == "__main__":
    # Get the worksheet
    sheet = get_worksheet("Messageboard", 0)
    print("getting data from sheet")
    # Get the cells in the first column
    values = sheet.col_values(1)

    # Read old vaues from last time
    filename = "log.csv"  # Log file to check previous data
    # TODO: check that the file actually exists
    with open(filename, "r") as f:  # Use ´with´ to ensure file is properly closed
        old_values = next(csv.reader(f))  # Get old values as a list, much easier to use

    # Check if there is any new data since last time
    if values != old_values:  # We can compare lists!
        write_to_e_paper(values)

        # Log new values
        with open(filename, "w") as csv:
            writer = csv.writer(csv)  # There is also a csv.writer
            writer.writerow(values)

    else:
        print("there was no new data")
