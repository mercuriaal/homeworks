import time
from correct_login import login, password
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest


class TestAuthorization(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://passport.yandex.ru/auth/")

    def test_correct_authorization(self):
        driver = self.driver
        element = driver.find_element_by_id("passp-field-login")
        element.send_keys(login)
        element.send_keys(Keys.ENTER)
        driver.implicitly_wait(1)
        element = driver.find_element_by_id("passp-field-passwd")
        element.send_keys(password)
        element = driver.find_element_by_class_name("Button2")
        element.click()
        time.sleep(1)
        self.assertIn("profile", self.driver.current_url)

    def test_wrong_existing_password(self):
        driver = self.driver
        element = driver.find_element_by_id("passp-field-login")
        element.send_keys(login)
        element.send_keys(Keys.ENTER)
        driver.implicitly_wait(1)
        element = driver.find_element_by_id("passp-field-passwd")
        element.send_keys("WrongExistingPassword")
        element = driver.find_element_by_class_name("Button2")
        element.click()
        time.sleep(1)
        self.assertNotIn("profile", self.driver.current_url)

    def test_non_existing_password(self):
        driver = self.driver
        element = driver.find_element_by_id("passp-field-login")
        element.send_keys(login)
        element.send_keys(Keys.ENTER)
        driver.implicitly_wait(1)
        element = driver.find_element_by_id("passp-field-passwd")
        element.send_keys("NonExistingPassword")
        element = driver.find_element_by_class_name("Button2")
        element.click()
        time.sleep(1)
        self.assertNotIn("profile", self.driver.current_url)

    def test_empty_password_field(self):
        driver = self.driver
        element = driver.find_element_by_id("passp-field-login")
        element.send_keys(login)
        element.send_keys(Keys.ENTER)
        driver.implicitly_wait(1)
        element = driver.find_element_by_id("passp-field-passwd")
        element.send_keys('')
        element = driver.find_element_by_class_name("Button2")
        element.click()
        time.sleep(1)
        self.assertNotIn("profile", self.driver.current_url)

    def test_non_existing_login(self):
        driver = self.driver
        element = driver.find_element_by_id("passp-field-login")
        element.send_keys("NonExistingLogin")
        element.send_keys(Keys.ENTER)
        driver.implicitly_wait(1)
        time.sleep(1)
        self.assertNotIn("welcome", self.driver.current_url)

    def tearDown(self):
        self.driver.close()


if __name__ == '__main__':
    unittest.main()
