# AccuWeather Allergies
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

_Creates sensors for Home Assistant with the AccuWeather Allergy level information for various sensor types_

## Installation

This app is best installed using
[HACS](https://github.com/custom-components/hacs), so that you can easily track and download updates.

Alternatively, you can download the `accu_allergies` directory from inside the `apps` directory here to your
local `apps` directory, then add the configuration to enable the `accu_allergies` module.

You will also need to install Beautiful Soup / bs4 and then copy the bs4 directory into the apps directory in Appdaemon or potentially (I haven't tried it) add bs4 to your python packages.

## How it works

The [AccuWeather](https://www.accuweather.com/) site provides this information, this just scrapes the page and makes the information available as a sensor in HA.

As this is non time critical sensor, it does not get the information on a set time schedule, but watches a input_boolean that you 
specify for when to update the sensor. You can obviously automate when you want that input_boolean to turn on.

### To Run

You will need to create an input_boolean entity to watch for when to update the sensor. When this
`input_boolean` is turned on, whether manually or by another automation you
create, the scraping process will be run to create/update the sensor.

To reduce the number of requests to the website, I have made this a two stage system, with one `input_boolean` controlling when
the data is requested from the website and a second when you want to update the sensors, meaning doing a HA restart won't trigger html requests, just reads from your file.

Therefore you will need to chain the two `input_boolean` requests so that one is offset by a minute to allow for the data to be downloaded.

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
```

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | | `accu_allergies`
`class` | False | string | | `Get_Accu_Allergies`
`ACC_FILE` | False | string | | path and name of a file to store html in, to reduce number of requests to the website
`ACC_FLAG` | False | string | | The name of the flag in HA for triggering getting the information from the website 
`DEB_FLAG` | False | string | | The name of the flag in HA for triggering refreshing the sensors from the stored html
`URL_ID` | False | string | | The id on the AccuWeather webpage for the node you want information for
`URL_CITY` | False | string | | The name on the AccuWeather webpage for the node you want information for
`URL_COUNTRY` | False | string | | The country code on the AccuWeather webpage for the node you want information for
`URL_LANG` | False | string | | The language code on the AccuWeather webpage for the node you want information for

## Issues/Feature Requests

Please log any issues or feature requests in this GitHub repository for me to review.