# NYT Access Renewal Script

The Multnomah County Library provides complimentary access to the New York Times for anyone with a library card. *Nice*, right? The down side is that you must reactivate the access frequently to maintain your subscription. This script will login and renew your subscription automatically so you don't have to.

## Installation

The script does not have an install, per se. You can simply clone this repo to the location of your choice and run from there. At a minimum, you'll need to do the following before executing the code:

1. Populate `env.env` with your library card number and pin
2. Rename `env.env` to `.env`
3. Install the requirements listed in requirements.txt 

If any of these items have not been completed prior to running the script will fail. 

> [!CAUTION]
> The `.env` file contains your library card and NYTimes login info, and potentially your pushover userkey and apikey. Once this file is configured you may want to restrict access so your sensitive info is not potentially exposed to other users on your machine, etc. On linux/mac you can use chmod to set the file perms to 400. 

## Configuration

There are a number of items that can be configured in the `.env` file. Only four are strictly required for this script to work:

- `MCL_CARDNUM` - Your Multnomah County Library library card number
- `MCL_CARDPIN` - Your Multnomah County Library pin number
- `NTY_EMAIL` - Your NYTimes.com username/email address
- `NYT_PASS` - Your NYTimes.com password
 
These are the same card and pin numbers you use to login to the library website and NYTimes.com. This script will not work if any of these items are not populated in `.env` or are invalid.

### Optional Configuration ###

The script is capable of Pushover alerting, however this is disabled by default. To enable populate the following items in .env with your information:

- `ALERTS=true` - This enables alerting
- `ALERT_PRIORITY=0` - This will determine the priority the alert is sent with. See [Pushover Message Priority](https://pushover.net/api#priority) for more info.
- `PUSH_USERKEY=yourpushoveruserkey` - Populate this with your pushover user key
- `PUSH_TOKEN=yourpushoverapitoken` - Populate this with your pushover api token

## Usage ##

The script does not accept any arguments. To launch simply activate your venv and run `python update_nytaccess.py`.

### Manually running ###

Below are a manual step-by-step instructions that may or may not work for you. The instructions below assume you're using linux, Mac, or some flavor of unixy OS.

1. Clone this repo to the location of your choosing.
2. From the command line, create a virtual environment, activate it, install requirements, and deactivate the virtual environment:
   - `cd update_nytaccess`
   - `python -m venv .pyenv`
   - `source .pyenv/bin/activate`
   - `pip install -r requirements.txt`
3. Launch the script: `python update_nytaccess.py`
4. Deactivate the virtual environment: `deactivate`

If all configuration options are correct and there were no errors you'll see something similar to this:

`2025-04-04 16:06 - INFO - Initializing NYT renewal script...`  
`2025-04-04 16:06 - INFO - NYT access renewal was successful!`

### Scheduling via cron ###
While there are a many ways to kick off a script, nearly all of my scripts run from a linux machine so my preferred method is to create a python virtual environment and using cron for scheduling. Cron is simple, straightforward, has been around for a million years, and virtually never fails. To schedule the script to run every morning at 6AM complete the steps below, making sure to modify the directories to fit your environment.

1. Open cron editor under your user account: `crontab -e`
2. Add the following line at the bottom of the file, making sure to modify the directories to fit your environment.:
   - `0 6 * * * cd /path/to/script/gitcloned && source .pyenv/bin/activate && python update_nytaccess.py && deactivate`
3. Save file and exit

> [!IMPORTANT]
> You will need to modify the path in the cron entry above to match the directory you're actually running from. In my case "cd /path/to/script/gitcloned" is changed to "/opt/scripts/nyt-library-update"

## Logging ##
Logging can be enable or disabled entirely by setting `ALERTS=` to true or false in `.env`. 

When running manually the script will log to the console as well as a log file located at logs/update.log. When scheduled with cron or otherwise automated the script will still log to logs/update.log. Logs will be rotated after they reach approximately 10MB in size. A total of 3 logs files will be rolled over. 

If you would like more or less logging this can be changed by modifying `maxBytes=` and `backupCount=` on line 22 to your preferred values. 
