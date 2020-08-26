import gspread
import os
import boto3
import json
from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials

# from dotenv import load_dotenv

# load_dotenv()
GET_HEADER = {
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET",
}
POST_HEADER = {
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST",
    "Access-Control-Allow-Credentials": True,
}


def getResponse(e):
    return {
        "statusCode": 200,
        "headers": GET_HEADER,
        "body": json.dumps({"message": str(e)}),
    }


def getErrorResponse(e):
    return {
        "statusCode": 400,
        "headers": GET_HEADER,
        "body": json.dumps({"message": str(e)}),
    }


def postResponse(e):
    return {
        "statusCode": 200,
        "headers": POST_HEADER,
        "body": json.dumps({"message": str(e)}),
    }


def postErrorResponse(e):
    return {
        "statusCode": 400,
        "headers": POST_HEADER,
        "body": json.dumps({"message": str(e)}),
    }


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
        self.document = self.gc.open(docname)
        try:
            self.worksheet = self.document.worksheet(worksheet)
        except Exception as e:
            role = worksheet.split("_")[0]
            if role in ["manager", "supervisor"]:
                self.worksheet = self.document.add_worksheet(
                    title=worksheet, rows="100", cols="20"
                )
                if role == "manager":
                    self.add(["user", "supervisor", "data", "status", "actionBy"])
                if role == "supervisor":
                    self.add(["user", "application", "data", "status", "manager"])
            else:
                print("Only managers and supervisors are allowed to make records!")

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

    def all(self,):
        return self.worksheet.get_all_records()


def get_user_role(event, context):
    try:
        user_role_wks = Sheet("joint-tables", "UserRole")
    except Exception as e:
        return getErrorResponse(e)
    return {
        "statusCode": 200,
        "headers": GET_HEADER,
        "body": json.dumps(user_role_wks.all()),
    }


def get_user_supervisor(event, context):
    try:
        user_supervisor_wks = Sheet("joint-tables", "UserSupervisor")
    except Exception as e:
        return getErrorResponse(e)
    return {
        "statusCode": 200,
        "headers": GET_HEADER,
        "body": json.dumps(user_supervisor_wks.all()),
    }


def get_applications(event, context):
    try:
        application_wks = Sheet("joint-tables", "Applications")
    except Exception as e:
        return getErrorResponse(e)
    return {
        "statusCode": 200,
        "headers": GET_HEADER,
        "body": json.dumps(application_wks.worksheet.get_all_values()),
    }


def get_manager_record(event, context):
    print(event)
    try:
        body = json.loads(event["body"])
        email = body["email"]
        user = email.split("@")[0]
        manager_wks = Sheet("manager_records", f"manager_{user}_records")
    except Exception as e:
        return postErrorResponse(e)
    return {
        "statusCode": 200,
        "headers": POST_HEADER,
        "body": json.dumps(manager_wks.all()),
    }


def get_supervisor_record(event, context):
    print(event)
    try:
        body = json.loads(event["body"])
        email = body["email"]
        user = email.split("@")[0]
        supervisor_wks = Sheet("supervisor_records", f"supervisor_{user}_records")
    except Exception as e:
        return postErrorResponse(e)
    return {
        "statusCode": 200,
        "headers": POST_HEADER,
        "body": json.dumps(supervisor_wks.all()),
    }


def reject_supervisor_record(event, context):
    print(event)
    try:
        body = json.loads(event["body"])
        row = body["row"]
        user = body["user"]
        status = body["status"]
    except Exception as e:
        print(e)
        return postErrorResponse(e)
    try:
        supervisor = user["email"].split("@")[0]
        print(supervisor)
        supervisor_wks = Sheet("supervisor_records", f"supervisor_{supervisor}_records")
        supervisor_wks.worksheet.update_cell(row, 4, status)
    except Exception as e:
        print(e)
        return postErrorResponse(e)
    return postResponse("Successfully rejected supervisor request")


def reject_manager_record(event, context):
    print(event)
    try:
        body = json.loads(event["body"])
        row = body["row"]
        user = body["user"]
        status = body["status"]
        application = body["application"]
    except Exception as e:
        print(e)
        return postErrorResponse(e)
    # try:
    #     manager = user["email"].split("@")[0]
    #     print(manager)
    #     manager_wks = Sheet("manager_records", f"manager_{manager}_records")
    #     manager_wks.worksheet.update_cell(row, 4, "rejected")
    # except Exception as e:
    #     print(e)
    #     return postErrorResponse(e)
    try:
        manager_wks = Sheet("manager_records", f"manager_{application}_records")
        print(manager_wks.all())
        manager_wks.worksheet.update_cell(row, 4, "rejected")
    except Exception as e:
        print(e)
        pass
    return postResponse("Successfully rejected manager request")


# deprecated, using access.approve_supervisor insread
# def approve_supervisor_record(event, context):
#     print(event)
#     try:
#         body = json.loads(event["body"])
#         row = body["row"]
#         user = body["user"]
#         supervisor = body["supervisor"]
#         data = body["data"]
#         applications = body["applications"]
#         status = body["status"]
#     except Exception as e:
#         print(e)
#         return postErrorResponse(e)

#     print("going to sheets")
#     success = []
#     if type(applications) == str:
#         applications = [applications]
#     # if want to change to pass to manager instead
#     for app in applications:
#         print(f"updating {app}'s manager record'")
#         try:
#             manager_wks = Sheet("manager_records", f"manager_{app}_records")
#             print(manager_wks.all())
#             manager_wks.add([user, supervisor, str(data), ""])
#         except Exception as e:
#             print(e)
#             pass
#         else:
#             success.append(app)
#     try:
#         a = success[0]
#         supervisor = supervisor.split("@")[0]
#         supervisor_wks = Sheet("supervisor_records", f"supervisor_{supervisor}_records")
#         supervisor_wks.worksheet.update_cell(row, 4, status)
#     except Exception as e:
#         print(e)
#         return postErrorResponse(e)
#     return postResponse(f"notified managers {str(success)}")


def approve_manager_record(event, context):
    print(event)
    print("getting user credentials")
    try:
        body = json.loads(event["body"])
        supervisor = body["supervisor"]
        user = body["user"]
        manager = body["manager"]
        data = body["data"]
        row = body["row"]
        application = body["application"]
    except Exception as e:
        print(e)
        return postErrorResponse(e)
    print("adding request to supervisor")
    try:
        supervisor = supervisor.split("@")[0]
        supervisor_wks = Sheet("supervisor_records", f"supervisor_{supervisor}_records")
        supervisor_wks.add([user, application, str(data), "", manager])
    except Exception as e:
        print(e)
        return postErrorResponse(e)
    else:
        try:
            manager_wks = Sheet("manager_records", f"manager_{application}_records")
            print(manager_wks.all())
            manager_wks.worksheet.update_cell(row, 4, "approved")
        except Exception as e:
            print(e)
            pass
    return postResponse("Successfully upped to supervisor")


def user_request(event, context):
    print(event)
    print("getting user credentials")
    try:
        body = json.loads(event["body"])
        applications = body["applications"]
        user = body["user"]
        data = body["data"]
        supervisor = user["supervisor"]
        if supervisor == "":
            return postErrorResponse("No supervisor found")
    except Exception as e:
        print(e)
        return postErrorResponse(e)

    print("adding request to manager")
    success = []
    for manager in applications:
        print(f"updating {manager}'s record'")
        try:
            manager_wks = Sheet("manager_records", f"manager_{manager}_records")
            manager_wks.add([user["email"], supervisor, str(data)])
        except Exception as e:
            print(e)
            pass
        else:
            success.append(manager)
    return postResponse(f"Successful request for {str(success)}")
