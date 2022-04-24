
## AppDaemon configuration

You will also need to install Beautiful Soup / bs4 by adding bs4 to your python packages in Appdaemon 4 configuration on the add-on panel.

```yaml
system_packages: []
python_packages:
  - bs4
init_commands: []
```

## App configuration

In the appdaemon/apps/apps.yaml file -

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
  WEB_VER: ""
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

