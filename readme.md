## NOTE - added automatic daily download 

# AccuWeather Allergies
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

_Creates sensors for Home Assistant with the AccuWeather Allergy level information for various sensor types_

## Lovelace Example

PRE APRIL22 changes

![Example of Allergies information in the Dashboard](https://github.com/simonhq/accu_allergies/blob/master/accu_allergies_glances.PNG)

APRIL22 changes

![Example of Allergies information in the Dashboard](https://github.com/simonhq/accu_allergies/blob/master/post_april22.jpg)

## Installation

This app is best installed using [HACS](https://github.com/custom-components/hacs), so that you can easily track and download updates.

Alternatively, you can download the `accu_allergies` directory from inside the `apps` directory here to your local `apps` directory, then add the configuration to enable the `accu_allergies` module.

## How it works

The [AccuWeather](https://www.accuweather.com/) site provides this information, this just scrapes the page and makes the information available as a sensor in HA.

As this is non time critical sensor, it only gets the information on a set time schedule, once per day at 5.07am, but it also watches an `input_boolean` that you specify for when to update the sensor. You can obviously automate when you want that input_boolean to turn on.

### To Run outside of the schedule

You will need to create an input_boolean entity to watch for when to update the sensor. When this `input_boolean` is turned on, whether manually or by another automation you create, the scraping process will be run to create/update the sensor.

To reduce the number of requests to the website, I have made this a two stage system, with one `input_boolean` controlling when the data is requested from the website and a second when you want to update the sensors, meaning doing a HA restart won't trigger html requests, it will just read from your saved data file from that morning.

Therefore you will need to chain the two `input_boolean` requests so that one is offset by a minute to allow for the data to be downloaded.

## AppDaemon configuration

You will also need to install Beautiful Soup / bs4 by adding bs4 to your python packages in Appdaemon.

```yaml
system_packages: []
python_packages:
  - bs4
init_commands: []
```

## App configuration

```yaml
accu_allergies:
  module: accu_allergies
  class: Get_Accu_Allergies
  ACC_FILE: "./allergies"
  ACC_FLAG: "input_boolean.get_allergies_data"
  DEB_FLAG: "input_boolean.reset_allergies_sensor"
  URL_ID: "21921"
  URL_CITY: "canberra"
  URL_COUNTRY: "au"
  URL_LANG: "en"
  URL_POSTCODE: ""
  WEB_VER: "" # or use "APRIL22"
```

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | | `accu_allergies`
`class` | False | string | | `Get_Accu_Allergies`
`ACC_FILE` | False | string | | path and name of a file to store html in, to reduce number of requests to the website
`ACC_FLAG` | False | string | | The name of the flag in HA for triggering getting the information from the website 
`DEB_FLAG` | False | string | | The name of the flag in HA for triggering refreshing the sensors from the stored html
`URL_ID` | False | string | | The ID on the AccuWeather webpage for the node you want information for
`URL_CITY` | False | string | | The name on the AccuWeather webpage for the node you want information for
`URL_COUNTRY` | False | string | | The country code on the AccuWeather webpage for the node you want information for
`URL_LANG` | False | string | | The language code on the AccuWeather webpage for the node you want information for
`URL_POSTCODE` | True | string | | Some locations use the postcode as well as an ID in the AccuWeather webpage URL this will default to the ID value if left blank
`WEB_VER` | True | string | | Some locations have transitioned to a new website template for AccuWeather - use "APRIL22" if your area has the new template

## Sensors to be created

This app will create sensors

* sensor.acc_data_last_sourced

Pre APRIL22

sensors for each of the types for today and tomorrow (24 in total)
ragweed pollen, grass pollen, tree pollen, mold, dust, air quality, common cold, flu, asthma, arthritis, migraine, sinus

each sensor is a rating from 1->10

The actual site holds 12 days of information for each of the 12 concepts, but I have only chosen to get the current day and the next day.

Post APRIL22

air quality for today and tomorrow

sensors for each of the types for today only

each sensor is a low->extreme

dust & dander, sinus pressure, asthma, grass pollen, ragweed pollen, tree pollen, mold, migraine, arthritis, common cold, flu, 
indoor pests, outdoor pests, mosquitos, outdoor entertaining, lawn mowing, composting, air travel, driving, fishing, running
golf, biking & cycling, beach & pool, stargazing, hiking


## Issues/Feature Requests

Please log any issues or feature requests in this GitHub repository for me to review.