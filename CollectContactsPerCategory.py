import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy import create_engine
from webdriver_manager.chrome import ChromeDriverManager

class CollectContactsPerCategory :

    def __init__(self, selected_category_index) :
        self.engine = create_engine('sqlite:///database.db', echo=True)
        self.category_engine = create_engine('sqlite:///data_counts_per_category.db', echo=True)

        self.category_index = selected_category_index
        self.browser = webdriver.Chrome(ChromeDriverManager().install())
        self.browser.get("https://app.uplead.com/login")
        self.categories_of_industry = {}
        self.all_categories_checkboxes = {}
        self.all_locations = {}
        self.all_types = {}
        self.parent_categories = {}
        self.all_categories_title = ["Agriculture","Mining","Construction","Manufacturing","Wholesale","Transportation","Retail","Finance, Insurance, Real Estate","Services","Public Administration","Nonclassifiable"]
        self.label = ""
        self.counts = 0
        self.current_data_counts_per_table = {}
        self.real_data_counts_per_category = {}
        self.dataCount = 0

    def get_current_saved_data(self) :
        self.counts
        existing_tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", self.engine)
        data_counts_per_category = pd.read_sql("SELECT child_category_name, child_category_count FROM children_data_count;", self.category_engine)
        if len(existing_tables) > 0 :
            for table in existing_tables["name"] :
                existing_data_count = len(pd.read_sql(f"select * from {table}", self.engine))
                self.current_data_counts_per_table[table] = existing_data_count
                self.counts += existing_data_count
        if len(data_counts_per_category) :
            for index, child_category_name in enumerate(data_counts_per_category['child_category_name']) :
                for child_category_count in data_counts_per_category['child_category_count'] :
                    self.real_data_counts_per_category[child_category_name.replace(" ", "_")] = data_counts_per_category['child_category_count'][index]

    def login(self) :
        email_input = WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        ).send_keys("bobiehornung77654@gmail.com")
        self.browser.find_elements_by_tag_name("input")[1].send_keys("qwe123QWE!@#")
        self.browser.find_element_by_tag_name("button").click()
        time.sleep(5)
        self.browser.get("https://app.uplead.com/contact-search")
        
    def get_records(self, page_number = 1, row_number = 0):
        print("get recoress page number", page_number, "label", self.label)
        person_presented = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "app-table__body__cell"))
        )

        number_of_entities = self.browser.find_element_by_class_name("pagination__total-text--bold").text
        number_of_pages = int("".join(number_of_entities.split(","))) // 100
        if (type(number_of_pages)) == "int" and (int(str(number_of_pages).split(".")[1]) > 0.5) :
            number_of_pages = round(number_of_pages);
        else :
            number_of_pages = round(number_of_pages) + 1

        if int("".join(number_of_entities.split(","))) > 100 : # pagination = 100
            self.browser.find_element_by_class_name("custom-select__wrapper").click()
            hundred_per_page = WebDriverWait(self.browser, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "custom-select__content-wrapper"))
            )
            dropdown_lists = self.browser.find_elements_by_class_name("custom-select__select-row")
            for dropdown_list in dropdown_lists :
                if dropdown_list.get_attribute("innerHTML") == "100" : dropdown_list.click()

        unit_person = number_of_pages/10

        if (type(unit_person)) == "int" and (int(str(unit_person).split(".")[1]) > 0.5) :
            unit_person = round(unit_person);
        else :
            unit_person = round(unit_person) + 1
        
        condi_array = []
        for k in range(unit_person) :
            condi_array.append(k*10)

        if page_number > 1 :
            self.browser.find_element_by_class_name("search-bar__search").find_element_by_tag_name("input").clear()
            self.browser.find_element_by_class_name("search-bar__search").find_element_by_tag_name("input").send_keys(str(page_number))
            time.sleep(2)
            self.browser.find_element_by_class_name("search-bar__search").find_element_by_tag_name("input").send_keys(Keys.ENTER)
        page_number_1 = page_number
        while(True) :
            WebDriverWait(self.browser, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "app-table__body__row"))
            )
            persons = self.browser.find_elements_by_class_name("app-table__body__row")
            if row_number > 0 :
                persons = persons[row_number: len(persons)]

            for index, person in enumerate(persons) :
                print(f" \n page number -> {page_number_1} : index -> {self.counts} \n")
                self.browser.implicitly_wait(2)
                self.set_person_data(person, page_number_1, page_number, index, row_number)
                self.counts += 1
            row_number = -1
            if page_number_1 == number_of_pages:
                break
            page_number_1 += 1
            self.browser.find_element_by_class_name("search-bar__search").find_element_by_tag_name("input").clear()
            self.browser.find_element_by_class_name("search-bar__search").find_element_by_tag_name("input").send_keys(str(page_number_1))
            time.sleep(2)
            self.browser.find_element_by_class_name("search-bar__search").find_element_by_tag_name("input").send_keys(Keys.ENTER)

    def set_person_data(self, person, page_number_1 = -1, page_number = -1, index = -1, row_number = -1) :
        print("set person data")
        tags_group = []
        person_link = ""
        company_link = ""
        try:
            tags_group = person.find_elements_by_tag_name("a")
        except:
            pass

        for element in tags_group:
            link = element.get_attribute("href")
            if link.__contains__("contact") :
                person_link = link
            elif link.__contains__("company") :
                company_link = link

        self.save_person_data(person_link, company_link, page_number_1, page_number, index, row_number)

    def save_person_data(self, person_link, company_link, page_number_1 = -1, page_number = -1, index = -1, row_number= -1):
        company_social_media_link = ""
        try :
            main_window = self.browser.current_window_handle
            self.browser.execute_script(f"window.open('{person_link}','_blank');")
            print("opened person link")
            self.browser.switch_to_window(self.browser.window_handles[1])
            user_card = WebDriverWait(self.browser, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "userCard"))
            )
            name = user_card.find_element_by_class_name("userCard__mainDesc-name").text
            print(f"!!!!!!!!!!! {name} !!!!!!!!!!!")
            title = user_card.find_element_by_class_name("userCard__mainDesc-position").text
            social_media_link = ""
            try:
                social_media_link = self.browser.find_element_by_class_name(
                    "userCard__socialMedia-wrapper").find_element_by_tag_name("a").get_attribute("href")
            except:
                social_media_link = None
                pass

            phone_number = user_card.find_element_by_class_name("userCard__phone-wrapper").text.split('\n')[1]
            location = user_card.find_element_by_class_name("userCard__location-wrapper").text
            profile_image_link = self.browser.find_element_by_tag_name("img").get_attribute("src")

            experience = None
            person_url = person_link
            error = False
            if (self.browser.page_source.__contains__("Experience")):
                try:
                    experience = self.browser.find_element_by_class_name("experienceCard__inner").text.replace("\n","").replace(",", " ")
                except:
                    error = True

            self.browser.close()
            self.browser.switch_to_window(main_window)

            # Crawling Company Link
            self.browser.execute_script(f"window.open('{company_link}','_blank');")
            print("opened company link")
            self.browser.switch_to_window(self.browser.window_handles[1])
            # browser.implicitly_wait(3)
            try:
                company_name = WebDriverWait(self.browser, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "companyCard__mainDesc-name"))
                ).text
                collapsable_items = self.browser.find_elements_by_class_name("companyCard__collapsible-item")
                company_phone = collapsable_items[1].text.replace("\n", " ").replace(",", " ")[5:]
                company_website = collapsable_items[3].text.replace("\n", " ").replace(",", " ")
                industry_tags = collapsable_items[4].text.split("\n")[1].split(",")
                alexa_ranking = collapsable_items[9].text.split("\n")[1]
                revenue = collapsable_items[10].text.split("\n")[1]
                time.sleep(0.1)
                fortune_ranking = collapsable_items[11].text.split("\n")[1:]
                employees = collapsable_items[12].text.split("\n")[1]
                year_founded = collapsable_items[13].text.split("\n")[1]
                country = collapsable_items[0].text.split("\n")[-1]
            except (NoSuchElementException, StaleElementReferenceException):
                error = True
                pass

            time.sleep(0.5)
            done = False

            try:
                description = self.browser.find_element_by_class_name("companyCard__desc").text.replace("\n","").replace(","," ")
            except:
                description = None

            try:
                technologies_used = ",".join(
                    self.browser.find_element_by_class_name("technologiesCard__inner").text.split("\n"))
            except:
                technologies_used = None

            try:
                company_social_media_link_group = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "socialLinks__item"))
                )
                company_social_media_links = company_social_media_link_group.find_elements_by_xpath("//a[contains(@class, 'socialLinks__item')]")
                for company_social_link in company_social_media_links :
                    if company_social_link.get_attribute('href').__contains__("linkedin.com") or company_social_link.get_attribute('href').__contains__("www.linkedin.com") :
                        company_social_media_link = company_social_link.get_attribute('href')

                competitors = ",".join(self.browser.find_element_by_class_name("competitors__inner").text.split("\n"))
            except:
                competitors = None
                company_social_media_links = None

            for index, sub_window in enumerate(self.browser.window_handles) :
                if index != 0 :
                    self.browser.switch_to_window(self.browser.window_handles[index])
                    self.browser.close()
            self.browser.switch_to_window(main_window)
            
            if error is False:
                data=[name, person_url, profile_image_link, social_media_link
                                , title, phone_number, location,
                                experience, company_name, company_link, ",".join(industry_tags), revenue,
                                employees, company_social_media_link, company_phone, company_website, alexa_ranking,
                                ",".join(fortune_ranking), year_founded, description, technologies_used, competitors, country]
                properties = ["Person First Name", "Person profile URL", "Person profile picture",
                                "Person linkedin URL"
                    , "Person title ", "Person phone",
                                "Person location",
                                "Person Experience", "Company Name", "Company URL", "Industry", "Revenue",
                                "Employees", "Company LinkedIn URL", "Company phone", "Company website",
                                "Alexa Ranking",
                                "Fortune ranking", "Year founded", "Description", "Technologies used", "Competitors",
                                "Country located"]
                
                print("!!! saving data ...");   
                data_frame = pd.DataFrame(data=[data], columns=properties)
                data_frame.to_sql(self.label, con=self.engine, if_exists='append', chunksize=1000)
        except : 
            print("error occured")
            print(person_link, company_link, page_number_1, page_number, index, row_number)
            for index, sub_window in enumerate(self.browser.window_handles) :
                if index != 0 :
                    self.browser.switch_to_window(self.browser.window_handles[index])
                    self.browser.close()
            self.browser.switch_to_window(main_window)
            if (page_number_1 > 0 and page_number > 0) and page_number == page_number_1 : 
                print("same saved page \n")
                page_number_index = 0
                if row_number > 0 and index > 0 :
                    page_number_index = row_number + index
                else :
                    page_number_index = index
                print("page_number_1, page_number_index-1", page_number_1, page_number_index-1)
                self.get_records(page_number_1, page_number_index-1)
            elif page_number > 0 and index > 0 :
                print("different current and saved page")
                print("page_number_1, page_number_index-1", page_number_1, index-1)
                self.get_records(page_number_1, index-1)

    def open_all_categories_of_industry(self) :
        for i in range(11):
            time.sleep(0.2)
            NOT_DONE_YET = True
            while NOT_DONE_YET:
                try:
                    category = WebDriverWait(self.browser, 15).until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                            "//*[@id=\"root\"]/div[1]/div[2]/div[2]/div/div[1]/div[1]/div[1]/div[2]/div[3]/div[1]/div/div/div/div/div/div[" + str(
                                i + 1) + "]/span/div/div[2]"))
                    ).click()
                    NOT_DONE_YET =False
                except:
                    pass

    def click_industry_first(self, i) :
        # industy_button
        industy_button = WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__item-name-wrapper"))
        )
        industy_buttons = self.browser.find_elements_by_class_name("filter__item-name-wrapper")
        industy_buttons[i].click()
        # By Industry Category
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__tree-subFilter-trigger"))
        )
        by_industry_category = self.browser.find_elements_by_class_name("filter__tree-subFilter-trigger")[0].find_element_by_tag_name("p")
        by_industry_category.click()

    def click_industry_next(self, i) :
        # industy_button
        industy_button = WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__item-name-wrapper"))
        )
        industy_buttons = self.browser.find_elements_by_class_name("filter__item-name-wrapper")
        industy_buttons[i].click()

    def clear_search(self) :
        try:
            clear_search_button = WebDriverWait(self.browser, 15).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id=\"root\"]/div[1]/div[2]/div[2]/div/div[2]/div/div[1]/div[2]/button[1]"))
            )
            clear_search_button.click()
        except:
            clear_all_criteria_btn = self.browser.find_element_by_class_name('filter__footer').find_elements_by_tag_name('button')[1]
            clear_all_criteria_btn.click()

    def get_all_location(self) :
        locations = WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__searchGroup-list"))
        )
        locations = self.browser.find_element_by_class_name('filter__searchGroup-list').find_elements_by_class_name('custom-checkbox__label')
        for index, location in enumerate(locations) :
            location_name = location.get_attribute("innerHTML")
            if location_name != "Select All" :
                self.all_locations[location_name] = index

    def get_all_categories_of_category(self) :
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "custom-checkbox__wrapper"))
        )
        all_categories = self.browser.find_elements_by_class_name('custom-checkbox__wrapper')
        for index, category in enumerate(all_categories) :
            category_title = category.find_element_by_tag_name('p').get_attribute('innerHTML')
            isCategory = category_title in self.all_categories_title
            if isCategory != True :
                self.all_categories_checkboxes[category_title] = index
            else :
                self.parent_categories[category_title] = index

    def get_all_types(self) :
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "custom-checkbox__label"))
        )
        all_type_elements = self.browser.find_elements_by_class_name('custom-checkbox__label')
        for index, type_elemenet in enumerate(all_type_elements) :
            type_name = type_elemenet.get_attribute("innerHTML")
            self.all_types[type_name] = index

    def click_type(self, categiry_checkbox, location) :
        self.clear_search()
        self.click_location(categiry_checkbox)
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__searchGroup-list"))
        )
        locations = self.browser.find_element_by_class_name('filter__searchGroup-list').find_elements_by_class_name('custom-checkbox__label')
        locations[location].click()
        self.click_industry_next(5)

    def get_all_fortune_ranking(self) :
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "custom-checkbox__label"))
        )
        all_type_elements = self.browser.find_elements_by_class_name('custom-checkbox__label')
        for index, type_elemenet in enumerate(all_type_elements) :
            type_name = type_elemenet.get_attribute("innerHTML")
            all_fortune_ranking[type_name] = index

    def search_with_location_and_type_and_fortune_ranking(self, categiry_checkbox, location, type_element) :
        self.clear_search()
        self.click_location(categiry_checkbox)
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__searchGroup-list"))
        )
        locations = self.browser.find_element_by_class_name('filter__searchGroup-list').find_elements_by_class_name('custom-checkbox__label')
        locations[location].click()
        self.click_industry_first(5)
        self.browser.implicitly_wait(1)
        all_type_elements = self.browser.find_elements_by_class_name('custom-checkbox__label')
        all_type_elements[type_element].click()
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__tree-subFilter-trigger"))
        )
        by_industry_category = self.browser.find_elements_by_class_name("filter__tree-subFilter-trigger")[1].find_element_by_tag_name("p")
        by_industry_category.click()
        self.get_all_fortune_ranking()
        for fortune_ranking in all_fortune_ranking :
            all_type_elements = self.browser.find_elements_by_class_name('custom-checkbox__label')
            done_button = self.browser.find_element_by_class_name("filter__tree-closeBtn")

            all_type_elements[all_fortune_ranking[fortune_ranking]].click()
            done_button.click()
            try :
                self.dataCount = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "pagination__total-text--bold"))
                )
                self.dataCount = self.browser.find_element_by_xpath('//span[contains(@class, "pagination__total-text--bold")]').get_attribute('innerHTML');
                self.dataCount = int(self.dataCount.replace(',', ''))
            except :
                self.dataCount = None
            self.get_records()

    def search_with_location_and_type(self, categiry_checkbox, location) :
        print("search_with_location_and_type -> ", categiry_checkbox, location)
        self.clear_search()
        self.click_location(categiry_checkbox)
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__searchGroup-list"))
        )
        locations = self.browser.find_element_by_class_name('filter__searchGroup-list').find_elements_by_class_name('custom-checkbox__label')
        locations[location].click()
        self.click_industry_first(5)
        self.browser.implicitly_wait(2)
        # get all types
        self.get_all_types()

        for type_element in self.all_types :
            all_type_elements = self.browser.find_elements_by_class_name('custom-checkbox__label')
            done_button = self.browser.find_element_by_class_name("filter__tree-closeBtn")
            all_type_elements[self.all_types[type_element]].click()
            done_button.click()
            try :
                self.dataCount = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "pagination__total-text--bold"))
                )
                self.dataCount = self.browser.find_element_by_xpath('//span[contains(@class, "pagination__total-text--bold")]').get_attribute('innerHTML');
                self.dataCount = int(self.dataCount.replace(',', ''))
            except:
                self.dataCount = None
            
            if (self.dataCount != None) and (self.dataCount > 100000) :
                search_with_location_and_type_and_fortune_ranking(categiry_checkbox, location, self.all_types[type_element])
            elif (self.dataCount != None) and (self.dataCount <= 100000) :
                self.get_records()
            self.click_type(categiry_checkbox, location)

    def click_location(self, categiry_checkbox) :
        self.clear_search()
        
        # click industry without By Industry Category
        self.click_industry_next(0)

        # open all categories of industry
        self.open_all_categories_of_industry()
        all_categories = self.browser.find_elements_by_class_name('custom-checkbox__wrapper')
        all_categories[categiry_checkbox].click()

        # click industry with By Industry Category
        self.click_industry_next(2)
        search_location = WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__searchGroup-input"))
        )
        self.browser.implicitly_wait(2)
        search_location.click()

    def search_with_location(self, categiry_checkbox) :
        # click industry, category, location
        self.clear_search()
        self.click_industry_next(0)

        self.open_all_categories_of_industry()
        all_categories = self.browser.find_elements_by_class_name('custom-checkbox__wrapper')
        all_categories[categiry_checkbox].click()
        self.click_industry_first(2)
        search_location = WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__searchGroup-input"))
        )
        self.browser.implicitly_wait(2)
        search_location.click()
        # get all locations
        self.get_all_location()
        WebDriverWait(self.browser, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "filter__searchGroup-list"))
        )
        locations = self.browser.find_element_by_class_name('filter__searchGroup-list').find_elements_by_class_name('custom-checkbox__label')
        done_button = self.browser.find_element_by_class_name("filter__tree-closeBtn")

        for location in self.all_locations :
            # search by location
            locations = self.browser.find_element_by_class_name('filter__searchGroup-list').find_elements_by_class_name('custom-checkbox__label')
            done_button = self.browser.find_element_by_class_name("filter__tree-closeBtn")
            locations[self.all_locations[location]].click()
            done_button.click()
            try :
                self.dataCount = WebDriverWait(self.browser, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "pagination__total-text--bold"))
                )
                self.dataCount = self.browser.find_element_by_xpath('//span[contains(@class, "pagination__total-text--bold")]').get_attribute('innerHTML');
                self.dataCount = int(self.dataCount.replace(',', ''))
            except:
                self.dataCount = None
            print("!!! data count !!!", self.dataCount)

            if (self.dataCount != None) and (self.dataCount > 100000) : # search with category, location, type
                self.search_with_location_and_type(categiry_checkbox, self.all_locations[location])
            elif (self.dataCount != None) and (self.dataCount <= 100000) : # search by location, category
                self.get_records()
            self.click_location(categiry_checkbox)

    def search_with_category(self) :
        for index, categiry_checkbox in enumerate(self.all_categories_checkboxes) :
            # done button
            try :
                done_button = self.browser.find_element_by_class_name("filter__tree-closeBtn")
            except :
                pass

            all_categories = self.browser.find_elements_by_class_name('custom-checkbox__wrapper')
            all_categories[self.category_index].click()
            self.label = all_categories[self.category_index].find_element_by_tag_name('p').get_attribute("innerHTML")
            self.label = self.label.replace(" ", "_")
            done_button.click()

            # calc data count
            self.dataCount = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pagination__total-text--bold"))
            )
            self.dataCount = self.browser.find_element_by_xpath('//span[contains(@class, "pagination__total-text--bold")]').get_attribute('innerHTML');
            self.dataCount = int(self.dataCount.replace(',', ''));

            if len(self.current_data_counts_per_table) > 0 and self.current_data_counts_per_table.__contains__(self.label) :
                current_saved_data_counts_of_this_category = self.current_data_counts_per_table[self.label]
                if self.dataCount >= current_saved_data_counts_of_this_category :
                    page_number = int(str(current_saved_data_counts_of_this_category/100).split(".")[0])
                    row_number = int(str(current_saved_data_counts_of_this_category/100).split(".")[1])
                    if page_number == 0 : page_number = 1
                    print("@@@@@@@@@@@@@@", page_number, row_number)
                    self.get_records(page_number, row_number)
            else :
                print("datacount, index", self.dataCount, index)
                if self.dataCount > 100000 : # search with category, location
                    self.search_with_location(self.category_index)
                else : # collect contacts
                    self.get_records()
            self.clear_search()
            self.click_industry_next(0)
            self.open_all_categories_of_industry()
