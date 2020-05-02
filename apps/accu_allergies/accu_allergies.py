############################################################
#
# This class aims to get the Allergies information from Accuweather
#
# written to be run from AppDaemon for a HASS or HASSIO install
#
# Written: 30/04/2020
# on windows use py -m pip install beautifulsoup4
# you will need to copy the bs4 folder into your appdaemon/apps folder
############################################################

############################################################
# 
# In the apps.yaml file you will need the following
# updated for your database path, stop ids and name of your flag
#
# accu_allergies:
#   module: accu_allergies
#   class: Get_Accu_Allergies
#   ACC_FILE: "./allergies"
#   ACC_FLAG: "input_boolean.get_allergies_data"
#   DEB_FLAG: "input_boolean.reset_allergies_sensor"
#   URL_ID: "21921"
#   URL_CITY: "canberra"
#   URL_COUNTRY: "au"
#   URL_LANG: "en"
#   global_dependencies:
#     - globals
#     - secrets
#
# https://www.accuweather.com/en/au/canberra/21921/allergies-weather/21921
# https://www.accuweather.com/en/au/canberra/21921/cold-flu-weather/21921
# https://www.accuweather.com/en/au/canberra/21921/asthma-weather/21921
# https://www.accuweather.com/en/au/canberra/21921/arthritis-weather/21921
# https://www.accuweather.com/en/au/canberra/21921/migraine-weather/21921
# https://www.accuweather.com/en/au/canberra/21921/sinus-weather/21921
#
############################################################

# import the function libraries for beautiful soup
from bs4 import BeautifulSoup
#from requests_html import HTMLSession
from os import path
import json
import datetime
import appdaemon.plugins.hass.hassapi as hass
import globals
import requests
import shelve

class Get_Accu_Allergies(hass.Hass):

    ACC_FLAG = ""
    DEB_FLAG = ""
    URL_LANG = ""
    URL_COUNTRY = ""
    URL_CITY = ""
    URL_ID = ""
    
    payload = {}
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    #"https://www.accuweather.com/URL_LANG/URL_COUNTRY/URL_CITY/URL_ID/cold-flu-weather/URL_ID"
    #url building
    url_base = "https://www.accuweather.com"
    url_txt_sets = [["/allergies-weather/","allergies"], ["/cold-flu-weather/","coldflu"], ["/asthma-weather/","asthma"], ["/arthritis-weather/","arthritis"], ["/migraine-weather/","migraine"], [ "/sinus-weather/","sinus"]]
    
    # run to setup the system
    def initialize(self):
        #get the info for the system
        self.ACC_FILE = globals.get_arg(self.args, "ACC_FILE")
        self.ACC_FLAG = globals.get_arg(self.args, "ACC_FLAG")
        self.DEB_FLAG = globals.get_arg(self.args, "DEB_FLAG")
        self.URL_LANG = globals.get_arg(self.args, "URL_LANG")
        self.URL_COUNTRY = globals.get_arg(self.args, "URL_COUNTRY")
        self.URL_CITY = globals.get_arg(self.args, "URL_CITY")
        self.URL_ID = globals.get_arg(self.args, "URL_ID")

        #create the original sensors
        self.load_sensors()

        #set the listener for the update flag for getting the data
        self.listen_state(self.get_all_data, self.ACC_FLAG, new="on")
        #set the listener for update flag for updating the sensor from the files
        self.listen_state(self.set_acc_sensors, self.DEB_FLAG, new="on")


    #get the information from each of the pages and write them into text files for reuse
    def get_all_data(self, entity, attribute, old, new, kwargs):
        #call the data builder
        self.get_html_data()
        #turn off the flag
        self.turn_off(self.ACC_FLAG)
    
    #request the website information
    def get_html_data(self):
        #build the url for the correct country and area
        start_url = self.url_base + "/" + self.URL_LANG + "/" + self.URL_COUNTRY + "/" + self.URL_CITY + "/" + self.URL_ID
        #for each of the allergy pages
        for sets in self.url_txt_sets:
            #build the url for this allergy type
            data_url = start_url + sets[0] + self.URL_ID
            #call the function to get the information and put it in the text file
            self.get_data(data_url, sets[1])
        
    #request the website information and write it to a file
    def get_data(self, url, txt):
        # request the rendered html
        self.log("request" + url)
        data_from_website = self.get_html(url) 
        # write the html into the local shelve file
        with shelve.open(self.ACC_FILE) as allergies_db:
            allergies_db[txt] = data_from_website
        #write out the get sensor
        self.set_get_sensor()
        #update the sensor
        self.create_get_sensor()

    def set_get_sensor(self):
        #create a sensor to keep track last time this was run
        tim = datetime.datetime.now()
        date_time = tim.strftime("%d/%m/%Y, %H:%M:%S")
        #add date time to the save file
        with shelve.open(self.ACC_FILE) as allergies_db:
            allergies_db["updated"] = date_time

    def create_get_sensor(self):
        #get last update date time from the save file 
        with shelve.open(self.ACC_FILE) as allergies_db:
            date_time = allergies_db["updated"]
        #create the sensor
        self.set_state("sensor.acc_data_last_sourced", state=date_time, replace=True, attributes={"icon": "mdi:timeline-clock-outline", "friendly_name": "ACC Allergy Data last sourced"})

    #get the html from the website
    def get_html(self, url):
        #create request for getting information from the accuweather website
        response = requests.request("GET", url, headers=self.headers, data = self.payload)
        #scrape and return the rendered html
        return response.text.encode('utf8')

    # call the processes to create the sensors
    def set_acc_sensors(self, entity, attribute, old, new, kwargs):
        #load all the sensors
        self.load_sensors()
        #turn off the flag
        self.turn_off(self.DEB_FLAG)


    def load_sensors(self):    
        #if no current data files
        with shelve.open(self.ACC_FILE) as allergies_db:
            if self.url_txt_sets[0][1] not in allergies_db:
                self.get_html_data()

        #create the sensors
        #pollens etc
        self.get_allergies_info(self.url_txt_sets[0][1])
        #cold and flu
        self.get_coldflu_info(self.url_txt_sets[1][1])
        #asthma
        self.get_asthma_info(self.url_txt_sets[2][1])
        #arthritis
        self.get_arthritis_info(self.url_txt_sets[3][1])
        #migraine
        self.get_migraine_info(self.url_txt_sets[4][1])
        #sinus
        self.get_sinus_info(self.url_txt_sets[5][1])
        #update the last updated sensor
        self.create_get_sensor()

        
    #get the info for pollens - ragweed, grass, tree, mold, dust and air quality
    def get_allergies_info(self, txt):

        #open the file and read the allergies information
        with shelve.open(self.ACC_FILE) as allergies_db:
            html_info = allergies_db[txt]
        #parse the file for the hmtl
        soup = BeautifulSoup(html_info, "html.parser")

        #get the 7th script block with the variables in it
        all_tags = soup.findAll('script')[2]
        #convert the soup variable into a string so we can manipulate
        tags = str(all_tags)
        #split by the 'var ' so we can get the correct variable values
        stags = tags.split("var ")
        #get the 3rd variable field from the list (lifestyle)
        stags = stags[2]
        #remove the js variable and ; so we get to the raw data
        stags = stags.replace("lifestyleForecast = ", "")
        stags = stags.replace(";", "")
        #convert to json
        jtags = json.loads(stags)

        #get the ragweed pollen info for today(d) and tomorrow(t)
        rag_val_d = jtags["ragweed-pollen"][0]["value"]
        rag_phr_d = jtags["ragweed-pollen"][0]["phrase"]
        rag_val_t = jtags["ragweed-pollen"][1]["value"]
        rag_phr_t = jtags["ragweed-pollen"][1]["phrase"]
        #get the grass pollen info for today(d) and tomorrow(t)
        gra_val_d = jtags["grass-pollen"][0]["value"]
        gra_phr_d = jtags["grass-pollen"][0]["phrase"]
        gra_val_t = jtags["grass-pollen"][1]["value"]
        gra_phr_t = jtags["grass-pollen"][1]["phrase"]
        #get the tree pollen info for today(d) and tomorrow(t)
        tre_val_d = jtags["tree-pollen"][0]["value"]
        tre_phr_d = jtags["tree-pollen"][0]["phrase"]
        tre_val_t = jtags["tree-pollen"][1]["value"]
        tre_phr_t = jtags["tree-pollen"][1]["phrase"]
        #get the mold info for today(d) and tomorrow(t)
        mol_val_d = jtags["mold"][0]["value"]
        mol_phr_d = jtags["mold"][0]["phrase"]
        mol_val_t = jtags["mold"][1]["value"]
        mol_phr_t = jtags["mold"][1]["phrase"]
        #get the dust and dander info for today(d) and tomorrow(t)
        dus_val_d = jtags["dust-dander"][0]["value"]
        dus_phr_d = jtags["dust-dander"][0]["phrase"]
        dus_val_t = jtags["dust-dander"][1]["value"]
        dus_phr_t = jtags["dust-dander"][1]["phrase"]
        #get the air-quality info for today(d) and tomorrow(t)
        air_val_d = jtags["air-quality"][0]["value"]
        air_phr_d = jtags["air-quality"][0]["phrase"]
        air_val_t = jtags["air-quality"][1]["value"]
        air_phr_t = jtags["air-quality"][1]["phrase"]

        #create the hassio sensors for today and tomorrow for ragweed
        self.set_state("sensor.acc_ragweed_pollen_today", state=rag_val_d, replace=True, attributes={"icon": "mdi:clover", "friendly_name": "Ragweed Pollen Today", "today_ragweed_value": rag_val_d , "today_ragweed_phrase": rag_phr_d })
        self.set_state("sensor.acc_ragweed_pollen_tomorrow", state=rag_val_t, replace=True, attributes={"icon": "mdi:clover", "friendly_name": "Ragweed Pollen Tomorrow", "tomorrow_ragweed_value": rag_val_t , "tomorrow_ragweed_phrase": rag_phr_t })

        #create the hassio sensors for today and tomorrow for grass
        self.set_state("sensor.acc_grass_pollen_today", state=gra_val_d, replace=True, attributes={"icon": "mdi:barley", "friendly_name": "Grass Pollen Today", "today_grass_value": gra_val_d , "today_grass_phrase": gra_phr_d })
        self.set_state("sensor.acc_grass_pollen_tomorrow", state=gra_val_t, replace=True, attributes={"icon": "mdi:barley", "friendly_name": "Grass Pollen Tomorrow", "tomorrow_grass_value": gra_val_t , "tomorrow_grass_phrase": gra_phr_t })

        #create the hassio sensors for today and tomorrow for tree
        self.set_state("sensor.acc_tree_pollen_today", state=tre_val_d, replace=True, attributes={"icon": "mdi:tree-outline", "friendly_name": "Tree Pollen Today", "today_tree_value": tre_val_d , "today_tree_phrase": tre_phr_d })
        self.set_state("sensor.acc_tree_pollen_tomorrow", state=tre_val_t, replace=True, attributes={"icon": "mdi:tree-outline", "friendly_name": "Tree Pollen Tomorrow", "tomorrow_tree_value": tre_val_t , "tomorrow_tree_phrase": tre_phr_t })

        #create the hassio sensors for today and tomorrow for mold
        self.set_state("sensor.acc_mold_today", state=mol_val_d, replace=True, attributes={"icon": "mdi:bacteria-outline", "friendly_name": "Mold Today", "today_mold_value": mol_val_d , "today_mold_phrase": mol_phr_d })
        self.set_state("sensor.acc_mold_tomorrow", state=mol_val_t, replace=True, attributes={"icon": "mdi:bacteria-outline", "friendly_name": "Mold Tomorrow", "tomorrow_mold_value": mol_val_t , "tomorrow_mold_phrase": mol_phr_t })

        #create the hassio sensors for today and tomorrow for dust
        self.set_state("sensor.acc_dust_today", state=dus_val_d, replace=True, attributes={"icon": "mdi:cloud-search-outline", "friendly_name": "Dust Today", "today_dust_value": dus_val_d , "today_dust_phrase": dus_phr_d })
        self.set_state("sensor.acc_dust_tomorrow", state=dus_val_t, replace=True, attributes={"icon": "mdi:cloud-search-outline", "friendly_name": "Dust Tomorrow", "tomorrow_dust_value": dus_val_t , "tomorrow_dust_phrase": dus_phr_t })

        #create the hassio sensors for today and tomorrow for air quality
        self.set_state("sensor.acc_air_today", state=air_val_d, replace=True, attributes={"icon": "mdi:air-purifier", "friendly_name": "Air Quality Today", "today_air_value": air_val_d , "today_air_phrase": air_phr_d })
        self.set_state("sensor.acc_air_tomorrow", state=air_val_t, replace=True, attributes={"icon": "mdi:air-purifier", "friendly_name": "Air Quality Tomorrow", "tomorrow_air_value": air_val_t , "tomorrow_air_phrase": air_phr_t })


    #get the info for cold and flu
    def get_coldflu_info(self, txt):

        #open the file and read the allergies information
        with shelve.open(self.ACC_FILE) as allergies_db:
            html_info = allergies_db[txt]
        #parse the file for the hmtl
        soup = BeautifulSoup(html_info, "html.parser")

        #get the 7th script block with the variables in it
        all_tags = soup.findAll('script')[2]
        #convert the soup variable into a string so we can manipulate
        tags = str(all_tags)
        #split by the 'var ' so we can get the correct variable values
        stags = tags.split("var ")
        #get the 3rd variable field from the list (lifestyle)
        stags = stags[2]
        #remove the js variable and ; so we get to the raw data
        stags = stags.replace("lifestyleForecast = ", "")
        stags = stags.replace(";", "")
        #convert to json
        jtags = json.loads(stags)

        #get the common cold info for today(d) and tomorrow(t)
        cco_val_d = jtags["common-cold"][0]["value"]
        cco_phr_d = jtags["common-cold"][0]["phrase"]
        cco_val_t = jtags["common-cold"][1]["value"]
        cco_phr_t = jtags["common-cold"][1]["phrase"]
        #get the influenza info for today(d) and tomorrow(t)
        flu_val_d = jtags["flu"][0]["value"]
        flu_phr_d = jtags["flu"][0]["phrase"]
        flu_val_t = jtags["flu"][1]["value"]
        flu_phr_t = jtags["flu"][1]["phrase"]
        
        #create the hassio sensors for today and tomorrow for common cold
        self.set_state("sensor.acc_common_cold_today", state=cco_val_d, replace=True, attributes={"icon": "mdi:snowflake-alert", "friendly_name": "Common Cold Today", "today_common_value": cco_val_d , "today_common_phrase": cco_phr_d })
        self.set_state("sensor.acc_common_cold_tomorrow", state=cco_val_t, replace=True, attributes={"icon": "mdi:snowflake-alert", "friendly_name": "Common Cold Tomorrow", "tomorrow_common_value": cco_val_t , "tomorrow_common_phrase": cco_phr_t })

        #create the hassio sensors for today and tomorrow for influenza
        self.set_state("sensor.acc_flu_today", state=flu_val_d, replace=True, attributes={"icon": "mdi:bacteria", "friendly_name": "Flu Today", "today_flu_value": flu_val_d , "today_flu_phrase": flu_phr_d })
        self.set_state("sensor.acc_flu_tomorrow", state=flu_val_t, replace=True, attributes={"icon": "mdi:bacteria", "friendly_name": "Flu Tomorrow", "tomorrow_flu_value": flu_val_t , "tomorrow_flu_phrase": flu_phr_t })


    #get the info for asthma
    def get_asthma_info(self, txt):

        #open the file and read the allergies information
        with shelve.open(self.ACC_FILE) as allergies_db:
            html_info = allergies_db[txt]
        #parse the file for the hmtl
        soup = BeautifulSoup(html_info, "html.parser")

        #get the 7th script block with the variables in it
        all_tags = soup.findAll('script')[2]
        #convert the soup variable into a string so we can manipulate
        tags = str(all_tags)
        #split by the 'var ' so we can get the correct variable values
        stags = tags.split("var ")
        #get the 3rd variable field from the list (lifestyle)
        stags = stags[2]
        #remove the js variable and ; so we get to the raw data
        stags = stags.replace("lifestyleForecast = ", "")
        stags = stags.replace(";", "")
        #convert to json
        jtags = json.loads(stags)

        #get the asthma info for today(d) and tomorrow(t)
        ast_val_d = jtags["asthma"][0]["value"]
        ast_phr_d = jtags["asthma"][0]["phrase"]
        ast_val_t = jtags["asthma"][1]["value"]
        ast_phr_t = jtags["asthma"][1]["phrase"]
        
        #create the hassio sensors for today and tomorrow for asthma
        self.set_state("sensor.acc_asthma_today", state=ast_val_d, replace=True, attributes={"icon": "mdi:lungs", "friendly_name": "Asthma Today", "today_asthma_value": ast_val_d , "today_asthma_phrase": ast_phr_d })
        self.set_state("sensor.acc_asthma_tomorrow", state=ast_val_t, replace=True, attributes={"icon": "mdi:lungs", "friendly_name": "Asthma Tomorrow", "tomorrow_asthma_value": ast_val_t , "tomorrow_asthma_phrase": ast_phr_t })


    #get the info for arthritis
    def get_arthritis_info(self, txt):

        #open the file and read the allergies information
        with shelve.open(self.ACC_FILE) as allergies_db:
            html_info = allergies_db[txt]
        #parse the file for the hmtl
        soup = BeautifulSoup(html_info, "html.parser")

        #get the 7th script block with the variables in it
        all_tags = soup.findAll('script')[2]
        #convert the soup variable into a string so we can manipulate
        tags = str(all_tags)
        #split by the 'var ' so we can get the correct variable values
        stags = tags.split("var ")
        #get the 3rd variable field from the list (lifestyle)
        stags = stags[2]
        #remove the js variable and ; so we get to the raw data
        stags = stags.replace("lifestyleForecast = ", "")
        stags = stags.replace(";", "")
        #convert to json
        jtags = json.loads(stags)

        #get the arthritis info for today(d) and tomorrow(t)
        art_val_d = jtags["arthritis"][0]["value"]
        art_phr_d = jtags["arthritis"][0]["phrase"]
        art_val_t = jtags["arthritis"][1]["value"]
        art_phr_t = jtags["arthritis"][1]["phrase"]
        
        #create the hassio sensors for today and tomorrow for arthritis
        self.set_state("sensor.acc_arthritis_today", state=art_val_d, replace=True, attributes={"icon": "mdi:bone", "friendly_name": "Arthritis Today", "today_arthritis_value": art_val_d , "today_arthritis_phrase": art_phr_d })
        self.set_state("sensor.acc_arthritis_tomorrow", state=art_val_t, replace=True, attributes={"icon": "mdi:bone", "friendly_name": "Arthritis Tomorrow", "tomorrow_arthritis_value": art_val_t , "tomorrow_arthritis_phrase": art_phr_t })


    #get the info for migraine
    def get_migraine_info(self, txt):

        #open the file and read the allergies information
        with shelve.open(self.ACC_FILE) as allergies_db:
            html_info = allergies_db[txt]
        #parse the file for the hmtl
        soup = BeautifulSoup(html_info, "html.parser")

        #get the 7th script block with the variables in it
        all_tags = soup.findAll('script')[2]
        #convert the soup variable into a string so we can manipulate
        tags = str(all_tags)
        #split by the 'var ' so we can get the correct variable values
        stags = tags.split("var ")
        #get the 3rd variable field from the list (lifestyle)
        stags = stags[2]
        #remove the js variable and ; so we get to the raw data
        stags = stags.replace("lifestyleForecast = ", "")
        stags = stags.replace(";", "")
        #convert to json
        jtags = json.loads(stags)

        #get the migraine info for today(d) and tomorrow(t)
        mig_val_d = jtags["migraine"][0]["value"]
        mig_phr_d = jtags["migraine"][0]["phrase"]
        mig_val_t = jtags["migraine"][1]["value"]
        mig_phr_t = jtags["migraine"][1]["phrase"]
        
        #create the hassio sensors for today and tomorrow for migraine
        self.set_state("sensor.acc_migraine_today", state=mig_val_d, replace=True, attributes={"icon": "mdi:head-flash", "friendly_name": "Migraine Today", "today_migraine_value": mig_val_d , "today_migraine_phrase": mig_phr_d })
        self.set_state("sensor.acc_migraine_tomorrow", state=mig_val_t, replace=True, attributes={"icon": "mdi:head-flash", "friendly_name": "Migraine Tomorrow", "tomorrow_migraine_value": mig_val_t , "tomorrow_migraine_phrase": mig_phr_t })

    
    #get the info for sinus
    def get_sinus_info(self, txt):

        #open the file and read the allergies information
        with shelve.open(self.ACC_FILE) as allergies_db:
            html_info = allergies_db[txt]
        #parse the file for the hmtl
        soup = BeautifulSoup(html_info, "html.parser")

        #get the 7th script block with the variables in it
        all_tags = soup.findAll('script')[2]
        #convert the soup variable into a string so we can manipulate
        tags = str(all_tags)
        #split by the 'var ' so we can get the correct variable values
        stags = tags.split("var ")
        #get the 3rd variable field from the list (lifestyle)
        stags = stags[2]
        #remove the js variable and ; so we get to the raw data
        stags = stags.replace("lifestyleForecast = ", "")
        stags = stags.replace(";", "")
        #convert to json
        jtags = json.loads(stags)

        #get the sinus info for today(d) and tomorrow(t)
        sin_val_d = jtags["sinus"][0]["value"]
        sin_phr_d = jtags["sinus"][0]["phrase"]
        sin_val_t = jtags["sinus"][1]["value"]
        sin_phr_t = jtags["sinus"][1]["phrase"]
        
        #create the hassio sensors for today and tomorrow for sinus
        self.set_state("sensor.acc_sinus_today", state=sin_val_d, replace=True, attributes={"icon": "mdi:head-remove-outline", "friendly_name": "Sinus Today", "today_sinus_value": sin_val_d , "today_sinus_phrase": sin_phr_d })
        self.set_state("sensor.acc_sinus_tomorrow", state=sin_val_t, replace=True, attributes={"icon": "mdi:head-remove-outline", "friendly_name": "Sinus Tomorrow", "tomorrow_sinus_value": sin_val_t , "tomorrow_sinus_phrase": sin_phr_t })

        