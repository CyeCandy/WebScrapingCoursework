#Parse 2014 MN Capital budget - https://www.revisor.mn.gov/laws/?year=2014&type=0&doctype=Chapter&id=294
#Store the summary in a DataFrame for eventual manipulation
from __future__ import print_function
import os.path
from collections import defaultdict
import string
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

filename = "MNBudget-2014.html"
url = "https://www.revisor.mn.gov/laws/?year=2014&type=0&doctype=Chapter&id=294"

def convert_num(val):
    """
    Convert the string number value to a float
     - Remove all extra whitespace
     - Remove commas
     - If wrapped in (), then it is negative number
    """
    val = string.strip(val).replace(",","").replace("(","-").replace(")","")
    return float(val)

# As we work through the process, it is easier to
# download it once and work with the saved copy instead of
# trying to hit the server each time
# Just delete the output file to force a new download
if os.path.isfile(filename):
    print("Loading the data via the file.")
    f = open(filename, 'r')
    c = f.read()
else:
    print("Fetching the data via the URL.")
    result = requests.get(url)
    c = result.content
    f = open(filename,'w')
    f.write(c)
f.close()

# Init the variables
# Use a defaultdict with an empty list because it eases the DataFrame creation
expense_lines = defaultdict(list)
funding_lines = defaultdict(list)
funding = False

# Now that we have the data, let's process it
soup = BeautifulSoup(c)

# After looking at the data, we can see that the summary has a div id we can use
summary = soup.find("div", {"class":"bill_section","id": "laws.1.1.0"})

# Get all the tables in the summary
tables = summary.find_all('table')

# The first table is not useful header info
# The second table contains all the we need (the list is 0 indexed)
data_table = tables[1]

#Go through each row of the table and pull out our data
for row in data_table.find_all("tr"):
    cells = row.find_all("td")
    # Ignore lines that don't have 3 cells of data because it is just spacing
    if len(cells) == 3:
        line = (string.strip(cells[0].text), convert_num(cells[2].text))
        # Once we get to the total line we start getting the funding lines
        if line[0] == "TOTAL":
            funding = True
            # We don't want to capture the total because we can calc it
            continue
        if funding:
            funding_lines[line[0]].append(line[1])
        else:
            expense_lines[line[0]].append(line[1])

# Create the DataFrame using from_dict
expense_df = pd.DataFrame.from_dict(expense_lines,orient='index')
funding_df = pd.DataFrame.from_dict(funding_lines,orient='index')
# Label our column
expense_df.rename(columns={0: 'Amount'}, inplace=True)
funding_df.rename(columns={0: 'Amount'}, inplace=True)

expense_df = expense_df.sort(columns='Amount')
funding_df = funding_df.sort(columns='Amount')

print(expense_df["Amount"].sum())
print(funding_df["Amount"].sum())

#Set some nicer defaults for plots
pd.options.display.mpl_style = 'default'

expense_bar = expense_df.plot(kind='barh', figsize=[7, 13],title="2014 MN Capital Budget Spending")
plt.savefig("MN-2014-Expense.png")

funding_bar = funding_df.plot(kind='barh',title="2014 MN Capital Budget Funding")
plt.savefig("MN-2014-Funding.png")