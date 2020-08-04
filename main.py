import gspread
import os
import boto3
import pandas as pd
from pprint import pprint
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials


load_dotenv()


class Sheet:
    def __init__(self, docname):
        # google credentials
        REGION = "ap-southeast-1"
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        filename = f'{os.environ.get("SAC_JSON_FILENAME")}.json'
        # session = boto3.Session()
        # s3_client = session.client("s3", region_name=REGION)
        # s3_client.download_file(
        #     "spreadsheet-crud-credentials", filename, f"/tmp/{filename}"
        # )
        credentials = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)
        self.gc = gspread.authorize(credentials)
        self.sheet = self.gc.open(docname).sheet1

    # def worksheet(self, docname):
    # worksheet
    # return self.wks

    def find(self, q):
        num_row = self.sheet.row_count
        x = num_row
        found = 0
        for i in range(1, num_row + 1):
            val = self.sheet.row_values(i)
            if val == []:
                break
            for j in range(1, len(val) + 1):
                if str(val[j - 1]).lower() == q:
                    return i, j
                    found = 1
                    break
        if not found:
            return None

    def add(self, email, sumtin):
        self.sheet.append_row([email, sumtin])

    def update(self, key, value):
        coord = self.find(key)
        if coord is None:
            return False
        y, x = coord
        value_cell = self.sheet.cell(y, x + 1)
        print(f"PREV VALUE - {value_cell.value}")
        self.sheet.update_cell(y, x + 1, value)
        print(f"CUR VALUE - {value}")
        return True

    def df(self):
        self.dataframe = pd.DataFrame(self.sheet.get_all_records())
        return dataframe


sheet = Sheet("yeet")
df = sheet.df()
pprint(df)
# sheet = mySheet.worksheet("yeet")
# sheet.add("jojonicho181@gmailc.om", "owner")
sheet.update("jojonicho181@gmail.com", "not owner")
pprint(df)

# pprint(sheet.findall("mario"))
# data = sheet.get_all_records()
# while x > 0:
#     val = sheet.row_values(x)
#     print(val)
# if(val == 'mario')
# row = sheet.row_values()
# sheet.append_row(["luigi", "peach"])
# sheet.find("mario")
# sheet.update_cell(sheet.findall("mario"), "not mario")

