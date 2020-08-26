import provider.papertrail_provider as papertrail
import provider.bitbucket_provider as bitbucket
import json
import boto3
from selenium import webdriver
from main import Sheet, POST_HEADER, GET_HEADER, postErrorResponse, postResponse
import ast


def bitbucket_onboard(manager, user, data):
    provider = bitbucket.BitbucketProvider(manager, user, data)
    provider.onboard()


def papertrail_onboard(manager, user, data):
    provider = papertrail.PapertrailProvider(manager, user)
    provider.onboard()


onboard_options = {
    "bitbucket": bitbucket_onboard,
    "papertrail": papertrail_onboard,
}


def manager_access(event, context):
    print(event)
    print("getting user credentials")
    try:
        body = json.loads(event["body"])
        applications = body["applications"]
        user = body["user"]
        data = body["data"]
        manager = body["manager"]
    except Exception as e:
        print(e)
        return postErrorResponse(e)
    success = []
    for app in applications:
        print(app)
        try:
            onboard_options[app](manager, user, data)
        except Exception as e:
            print(e)
        else:
            success.append(app)
    return postResponse(f"Successful request for {str(success)}")


def approve_supervisor_record(event, context):
    # event["body"] = event["body"].replace("\\", "")
    # event["body"] = event["body"].replace("\\", "")
    print(event)
    try:
        body = json.loads(event["body"])
        row = body["row"]
        user = body["user"]
        supervisor = body["supervisor"]
        manager = body["manager"]
        # data = body["data"].replace("'", '"')
        # print(data["bitbucket"])
        data = ast.literal_eval(body["data"])
        # print(x)
        # data = json.loads(x)
        print(data["bitbucket"])
        applications = body["applications"]
        status = body["status"]
        if type(applications) == str:
            applications = [applications]

    except Exception as e:
        print(e)
        return postErrorResponse(e)

    success = []
    for app in applications:
        print(f"onboarding {app}")
        try:
            onboard_options[app](manager, user, data)
        except Exception as e:
            print(f"error {app} - {e}")
        else:
            print(f"success {app}")
            success.append(app)
    try:
        a = success[0]
        supervisor = supervisor.split("@")[0]
        supervisor_wks = Sheet("supervisor_records", f"supervisor_{supervisor}_records")
        supervisor_wks.worksheet.update_cell(row, 4, status)
        supervisor_wks.worksheet.update_cell(row, 5, manager)
    except Exception as e:
        print(e)
        return postErrorResponse(e)
    return postResponse(f"notified managers {str(success)}")


# request and then go to supervisor, DEPRECATED
def request(event, context):
    # key = json.loads(get_secret())["PRIVATE_KEY"]
    print(event)
    print("getting user credentials")
    try:
        body = json.loads(event["body"])
        services = body["services"]
        user = body["user"]
        credentials = body["credentials"]
        print(credentials)
    except Exception as e:
        print(e)
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json",
            },
            "body": "queryStringParameters or body not included sufficient data",
        }
    print("going to sheets")
    try:
        supervisor = user["supervisor"]
        if supervisor == "":
            return {
                "statusCode": 200,
                "headers": POST_HEADER,
                "body": "No supervisor found",
            }
    except Exception as e:
        print(e)
        return {"statusCode": 200, "headers": POST_HEADER, "body": str(e)}
    print("adding request to supervisor")
    try:
        supervisor = supervisor.split("@")[0]
        supervisor_wks = Sheet("supervisor_records", f"supervisor_{supervisor}_records")
        supervisor_wks.add([user["email"], str(services), str(credentials)])
    except Exception as e:
        print(e)
        return {"statusCode": 200, "headers": POST_HEADER, "body": str(e)}
    return {
        "statusCode": 200,
        "headers": POST_HEADER,
        "body": "Successfully upped to supervisor",
    }
