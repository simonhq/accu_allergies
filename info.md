
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

## Sensors to be created

This app will create 25 sensors

* sensor.acc_data_last_sourced
* sensor.acc_ragweed_pollen_today
* sensor.acc_ragweed_pollen_tomorrow
* sensor.acc_grass_pollen_today
* sensor.acc_grass_pollen_tomorrow
* sensor.acc_tree_pollen_today
* sensor.acc_tree_pollen_tomorrow
* sensor.acc_mold_today
* sensor.acc_mold_tomorrow
* sensor.acc_dust_today
* sensor.acc_dust_tomorrow
* sensor.acc_air_today
* sensor.acc_air_tomorrow
* sensor.acc_common_cold_today
* sensor.acc_common_cold_tomorrow
* sensor.acc_flu_today
* sensor.acc_flu_tomorrow
* sensor.acc_asthma_today
* sensor.acc_asthma_tomorrow
* sensor.acc_arthritis_today
* sensor.acc_arthritis_tomorrow
* sensor.acc_migraine_today
* sensor.acc_migraine_tomorrow
* sensor.acc_sinus_today
* sensor.acc_sinus_tomorrow

The actual site holds 12 days of information for each of the 12 concepts, but I have only chosen to get the current day and the next day.