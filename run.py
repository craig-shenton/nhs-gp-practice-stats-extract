# Python source
# -------------------------------------------------------------------------
# Copyright (c) 2023 Craig Shenton. All rights reserved.
# Licensed under the MIT License. See license.txt in the project root for
# license information.
# -------------------------------------------------------------------------

"""
FILE:           run.py
DESCRIPTION:    Download and extract files from NHS Digitals publication "Patients Registered at a GP Practice"
CONTRIBUTORS:   Craig Shenton
CONTACT:        craig.shenton@ukhsa.gov.uk
CREATED:        07 Sept 2023
VERSION:        0.0.1
"""

from datetime import datetime
import requests
from bs4 import BeautifulSoup
import zipfile
import io
import pandas as pd
import os

def download_and_convert_to_tsv(target_strings, output_dir):
    """
    Downloads specific zip files from a web page, extracts their content, converts them to TSV format, and saves them.

    Args:
        target_strings (list): A list of specific strings to search for in the zip file names.
        output_dir (str): The directory where the TSV files will be saved.
    """
    try:
        current_date = datetime.now()
        month_year_variable = current_date.strftime('%B-%Y').lower()

        # Construct the URL based on the current date
        url = f"https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice/{month_year_variable}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/100.0'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "lxml")

        for target_string in target_strings:
            # Find the zip file containing the target string
            zip_link = soup.find("a", href=lambda href: href and target_string in href)

            if zip_link:
                # Get the URL of the zip file
                zip_url = zip_link['href']
                
                # Extract the zip file
                response = requests.get(zip_url)
                with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_ref:
                    zip_ref.extractall(output_dir)

                # Assuming the zip file contains a CSV file, read it and convert to TSV
                csv_filename = os.path.basename(zip_url)[:-4] + ".csv"  # Remove .zip and add .csv extension
                csv_path = os.path.join(output_dir, csv_filename)
                tsv_filename = target_string + ".tsv"
                tsv_path = os.path.join(output_dir, tsv_filename)

                gp_pop_df = pd.read_csv(csv_path, low_memory=False)
                gp_pop_df.to_csv(tsv_path, sep='\t', index=False)

                print(f"Downloaded and converted to TSV: {tsv_path}")
            else:
                print(f"No zip file containing '{target_string}' found on the page for {month_year_variable}.")

    except requests.exceptions.RequestException as e:
        print(f"HTTPError: {e}")

if __name__ == "__main__":
    # Specify a list of target strings and the output directory
    target_strings = ["gp-reg-pat-prac-sing-age-regions",
                      "gp-reg-pat-prac-sing-age-female", 
                      "gp-reg-pat-prac-sing-age-male"]
    output_directory = 'output/'

    download_and_convert_to_tsv(target_strings, output_directory)
