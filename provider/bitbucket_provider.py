import provider.onboard_provider as op
from selenium.webdriver.common.keys import Keys
import os


class BitbucketProvider(op.OnboardProvider):
    HOME_URL = "https://bitbucket.org"

    def __init__(self, manager, user, data):
        op.OnboardProvider.__init__(self)
        try:
            self.credentials = data
            self.user = user
            self.manager = manager
            self.repo = data["bitbucketRepository"]
            self.WORKSPACE_DEVELOPER_URL = f"https://bitbucket.org/{self.repo}/workspace/settings/groups/developers"
            print(manager, user, data)
        except Exception as e:
            print(f"Bitbucket Provider - {e}")

    def onboard(self):
        driver = self.setup_driver()
        print("\n- Start onboarding Bitbucket")

        try:
            # for now only sends email
            # self.sign_in(driver)
            # self.go_to_teams(driver)
            # self.invite_users(driver)
            self.send_email(
                "bitbucket", self.WORKSPACE_DEVELOPER_URL, self.user, self.manager,
            )
            print("- Finish onboarding Bitbucket")
        except Exception as e:
            print("- Error: " + str(e))
        finally:
            driver.close()
            driver.quit()

    # def sign_in(self, driver):
    #     driver.get(self.HOME_URL)
    #     print("- Visit Bitbucket Home page")

    #     self.smart_delay(lambda: driver.find_element_by_link_text("Log in"))

    #     login_link = driver.find_element_by_link_text("Log in").get_attribute("href")
    #     driver.get(login_link)
    #     print("- Visit Login page")

    #     self.smart_delay(lambda: driver.find_element_by_id("username"))
    #     print("- Sign In Bitbucket")

    #     username_input = driver.find_element_by_id("username")
    #     username_input.send_keys(os.environ["BITBUCKET_USERNAME"].strip())
    #     print("- Filling username")

    #     driver.find_element_by_xpath('//span[text()="Continue"]').click()
    #     print("- Click continue")

    #     self.smart_delay(lambda: driver.find_element_by_id("password"))

    #     password_input = driver.find_element_by_id("password")
    #     password_input.send_keys(os.environ["BITBUCKET_PASSWORD"].strip())
    #     print("- Filling password")

    #     self.smart_delay(lambda: driver.find_element_by_id("login-submit"))

    #     driver.find_element_by_id("login-submit").click()
    #     print("- Submit login form")

    # def go_to_teams(self, driver):
    #     self.smart_delay(lambda: driver.find_element_by_id("profileGlobalItem"), 35)

    #     driver.find_element_by_id("profileGlobalItem").click()
    #     print("- Click Profile menu")

    # def invite_users(self, driver):
    #     print("- Visit Workspace Developer")
    #     driver.get(self.WORKSPACE_DEVELOPER_URL)

    #     email_input = driver.find_element_by_id("group-add-member")
    #     email_input.send_keys(self.email)

    #     add_member = driver.find_element_by_css_selector("button.aui-button.add-button")
    #     add_member.click()
    #     self.delay(1)
    #     print("- Invited " + self.email)
