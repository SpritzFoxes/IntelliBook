from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime
import re
import sys
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 800))  
display.start()

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path
chrome_options = webdriver.ChromeOptions()    
# Add your options as needed    
options = [
  # Define window size here
  "--headless"
  "--window-size=1200,1200",
  "--ignore-certificate-errors"
 
    #"--headless",
    #"--disable-gpu",
    #"--window-size=1920,1200",
    #"--ignore-certificate-errors",
    #"--disable-extensions",
    #"--no-sandbox",
    #"--disable-dev-shm-usage",
    #'--remote-debugging-port=9222'
]

for option in options:
    chrome_options.add_argument(option)

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)


sheet_link = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFlGfAH9mUXWHp-MCXhS3hcHAaSmGN4ERo80osEgYP9crJGBLtSoOVOEqvUYRACc6mfqXXGHjMl0gV/pubhtml"

#date time in gg/mm/yy format
#current_date = datetime.now().strftime("%x")
current_date = "24/04/24"

# Convert to "yyyy-mm-dd" format
book_day = datetime.strptime(current_date, "%d/%m/%y").strftime("%Y-%m-%d")

participants_identifier = None

R_username = "raffy.p15@gmail.com"
R_passsword = "intelli15"

book_hour = ""
number_of_participants = ""
participant_names = []

day_link = "https://gyms.vertical-life.info/it/intellighenzia-project-asd/checkins#/service/custom-1/74/" + book_day

#XPATH with f for formatting; * used to select items regardless of tags

def get_max_th_id(driver, current_date):
    
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, f"//*[contains(text(), '{current_date}')]")))
    
    booked_date_td = driver.find_elements(By.XPATH, f"//*[contains(text(), '{current_date}') and not(following-sibling::td[text()='Yes'])]")
    deleted_date_td = driver.find_elements(By.XPATH, f"//*[contains(text(), '{current_date}') and (following-sibling::td[text()='Yes'])]")
    matching_td_elements = []
    
    for deleted_element in deleted_date_td:
        deleted_hour = deleted_element.find_element(By.XPATH, "./following-sibling::td").text
        deleted_participant = deleted_element.find_element(By.XPATH, "./following-sibling::td/following-sibling::td").text
        deleted_th_id = int(deleted_element.find_element(By.XPATH, "./preceding-sibling::th").get_attribute('id').split('R')[1])

        for booked_element in booked_date_td:
            booked_hour = booked_element.find_element(By.XPATH, "./following-sibling::td").text
            booked_participant = booked_element.find_element(By.XPATH, "./following-sibling::td/following-sibling::td").text

            booked_th_id = int(booked_element.find_element(By.XPATH, "./preceding-sibling::th").get_attribute('id').split('R')[1])

        if booked_hour == deleted_hour and booked_participant == deleted_participant and booked_th_id < deleted_th_id:
            matching_td_elements.append(booked_element)

    booked_date_td = [element for element in booked_date_td if element not in matching_td_elements]

    max_th_id = 0
    max_id_th_element = None
    for element in booked_date_td:
        tr = element.find_element(By.XPATH, "./ancestor::tr")

        th_elements = tr.find_elements(By.XPATH, ".//*[@id]")

        for element in th_elements:
            th_id = element.get_attribute('id')
            # If th_id contains 'R' and the part after 'R' is a number
            if 'R' in th_id and th_id.split('R')[1].isdigit():
                # Update max_th_id and max_id_th_element
                current_th_id = int(th_id.split('R')[1])
                if current_th_id > max_th_id:
                    max_th_id = current_th_id
                    max_id_th_element = th_id

    return max_id_th_element if max_th_id > 0 else None

def check_participants(driver, max_th_id):
    # Find the th with the max_th_id
    th_max_element = driver.find_element(By.XPATH, f"//*[@id='{max_th_id}']")

    parent_tr = th_max_element.find_element(By.XPATH, "./parent::tr")

    td_elements = parent_tr.find_elements(By.TAG_NAME, "td")

    participants_identifier = None
    for td in td_elements:
        if "R + V" in td.text:
            participants_identifier = 3
            break
        elif "V" in td.text:
            participants_identifier = 2
        elif "R" in td.text:
            participants_identifier = 1

    if participants_identifier is None:
        print("No participant found.")
        sys.exit()
        return None

    return participants_identifier

def find_following_td_text(driver, known_id, known_date_text):
    # Find the th with the known id
    th = driver.find_element(By.XPATH, f"//*[@id='{known_id}']")

    # Get the parent tr of this th
    tr = th.find_element(By.XPATH, "./ancestor::tr")

    # Find the td with the hour text
    hour_td = tr.find_element(By.XPATH, f".//td[contains(text(), '{known_date_text}')]")
    
    # Find the subsequent td
    subsequent_td = hour_td.find_element(By.XPATH, "./following-sibling::td")

    # Return the text of the subsequent td
    return subsequent_td.text

def choose_participant():
    if participants_identifier == 1:
        return ["Raffaele Papa"]
    elif participants_identifier == 2:
        return ["Veronica Zani"]
    elif participants_identifier == 3:
        return ["Raffaele Papa", "Veronica Zani"]
    print(participant_names)

def choose_participant_number():
    if participants_identifier == 1:
        return 1
    elif participants_identifier == 2:
        return 1
    elif participants_identifier == 3:
        return 2
    

def int_login(driver, username, password):
    driver.get(day_link)

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="login_link"]'))
    )

    login_button = driver.find_element(By.XPATH, '//*[@id="login_link"]')
    login_button.click()


    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
    )

    username_form = driver.find_element(By.XPATH, '//*[@id="username"]')
    username_form.send_keys(f"{username}")

    password_form = driver.find_element(By.XPATH, '//*[@id="password"]')
    password_form.send_keys(f"{password}" + Keys.ENTER)

    driver.get(day_link)

"""
#loop for waiting 12:00
def loop_till_12():
    while True:
        current_time = datetime.now().strftime('%H:%M')
        if current_time == '12:00':
            break
        time.sleep(2)
"""

def booking_the_hour():

    WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f'//div[@class="h3 mb-1" and text()="{book_hour}"]'))
            )

    hour_div = driver.find_element(By.XPATH, f'//div[@class="h3 mb-1" and text()="{book_hour}"]')

    hour_div_parent1 = hour_div.find_element(By.XPATH,'..')

    hour_div_parent2 = hour_div_parent1.find_element(By.XPATH,'..')

    select_element = Select(hour_div_parent2.find_element(By.CLASS_NAME, 'custom-select'))
    select_element.select_by_value(f'{number_of_participants}')

    book_button = hour_div_parent2.find_element(By.CLASS_NAME, 'btn-primary')
    book_button.click()

def booking_the_participants():

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, "label"))
    )

    for participant_name in participant_names:
        # Find the div with the known text
        div = driver.find_element(By.XPATH, f"//div[text()='{participant_name}']")

        # Find the parent of this div
        parent_div = div.find_element(By.XPATH, "..")

        # Find the parent of the parent div
        grandparent_div = parent_div.find_element(By.XPATH, "..")

        # Find the label inside the grandparent div
        label = grandparent_div.find_element(By.TAG_NAME, "label")

        driver.execute_script("arguments[0].click();", label)
        
    WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Continua']"))
            )

    continue_button = driver.find_element(By.XPATH, "//button[normalize-space()='Continua']")
    continue_button.click()

    #prenotazione finale
    WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Prenota']"))
            )

    final_book_button = driver.find_element(By.XPATH, "//button[normalize-space()='Prenota']")
    print(final_book_button.get_attribute('class'))
    with open('./GitHub_Action_Results.txt', 'w') as f:
      f.write(f"This was written with a GitHub action {driver.title}")
    #final_book_button.click()

driver.get(sheet_link)

max_th_id = get_max_th_id(driver, current_date)

participants_identifier = check_participants(driver, max_th_id)

participant_names = choose_participant()

number_of_participants = choose_participant_number()

book_hour = find_following_td_text(driver, max_th_id, current_date)

int_login(driver, R_username, R_passsword)

#loop_till_12()

booking_the_hour()

booking_the_participants()

time.sleep(10)

driver.quit()

