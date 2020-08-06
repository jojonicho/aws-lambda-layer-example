import gspread
import os
import boto3
import json
from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials


class Sheet:
    def __init__(self, docname, worksheet):
        # google credentials
        REGION = "ap-southeast-1"
        SCOPE = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
            # "https://www.googleapis.com/auth/admin.directory.user",
        ]
        FILENAME = f'{os.environ.get("SAC_JSON_FILENAME")}.json'
        session = boto3.Session()
        s3_client = session.client("s3", region_name=REGION)
        s3_client.download_file(
            "spreadsheet-crud-credentials", FILENAME, f"/tmp/{FILENAME}"
        )
        CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(FILENAME, SCOPE)
        self.gc = gspread.authorize(CREDENTIALS)
        self.worksheet = self.gc.open(docname).worksheet(worksheet)

    def find(self, q):
        num_row = self.worksheet.row_count
        x = num_row
        found = 0
        for i in range(1, num_row + 1):
            val = self.worksheet.row_values(i)
            if val == []:
                break
            for j in range(1, len(val) + 1):
                if str(val[j - 1]).lower() == q:
                    return i, j
                    found = 1
                    break
        if not found:
            return None

    # def find_email(self, q):
    #     df = self.df()
    #     indexes = df[df["email"] == q].index
    #     if len(indexes) >= 1:
    #         return indexes[0]
    #     return None

    # def find_all_email(self, q):
    #     df = self.df()
    #     indexes = df[df["email"] == q].index
    #     if len(indexes) >= 1:
    #         return indexes
    #     return None

    def add(self, row):
        self.worksheet.append_row(row)

    def update(self, key, value):
        coord = self.find(key)
        if coord is None:
            return False
        y, x = coord
        value_cell = self.worksheet.cell(y, x + 1)
        print(f"PREV VALUE - {value_cell.value}")
        self.worksheet.update_cell(y, x + 1, value)
        print(f"CUR VALUE - {value}")
        return True

    # def update(self, key, value):
    #     y = self.find_email(key)
    #     if y is None:
    #         return False
    #     value_cell = self.worksheet.cell(y, 2)
    #     print(f"PREV VALUE - {value_cell.value}")
    #     # pandas 0 indexing, +2 -> header + 1 based
    #     self.sheet.update_cell(y + 2, 2, value)
    #     print(f"CUR VALUE - {value}")
    #     return True

    def delete(self, key):
        coord = self.find(key)
        if coord is None:
            return False
        y, x = coord
        self.delete_rows(y)
        return True

    def delete_rows(self, start, end=-1):
        # add condition if rank is owner, cannot delete
        if end == -1:
            self.worksheet.delete_rows(start)
        # else:
        #     self.sheet.delete_rows(start, end)

    # def df(self):
    #     self.dataframe = pd.DataFrame(self.worksheet.get_all_records())
    #     return self.dataframe

    def all(self,):
        return self.worksheet.get_all_records()


def get_user_role(event, context):
    try:
        user_role_wks = Sheet("joint-tables", "UserRole")
    except Exception as e:
        return {"statusCode": 200, "body": str(e)}
    return {"statusCode": 200, "body": json.dumps(user_role_wks.all())}


def get_user_supervisor(event, context):
    try:
        user_supervisor_wks = Sheet("joint-tables", "UserSupervisor")
    except Exception as e:
        return {"statusCode": 200, "body": str(e)}
    return {"statusCode": 200, "body": json.dumps(user_supervisor_wks.all())}


# role_application_wks = Sheet("joint-tables", "RoleApplication")
# user_role_wks = Sheet("joint-tables", "UserRole")
# application_manager_wks = Sheet("joint-tables", "ApplicationManager")
# user_supervisor_wks = Sheet("joint-tables", "UserSupervisor")

# worksheets = [
#     role_application_wks,
#     user_role_wks,
#     application_manager_wks,
#     user_supervisor_wks,
# ]


# sheet.delete_rows(2)
# sheet.add(["myemaik4", "something"])
# sheet.delete("myemaik4")
# sheet.update("jojonicho181@gmail.com", "not owner")
# df = user_role_wks.df()
# pprint(df)

# for wks in worksheets:
#     pprint(wks.all())
# pprint(user_role_wks.all())

# print(sheet.find_email("jojonicho181@gmail.com"))

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

