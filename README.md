# An anonymous chatting platform inside Telegram application.
##########################################################

# Description
Using flask framework, using local files / mongo database to store data and telegram open API to facilate anonymous chatting among telegram users.

# Deployment
1. ## Clone/Fork this repository
2. ## Assets
   - Choose whether you want database approach or local files approach
   - Dpending on this use one of the two files of code
   - Create messages and users collections in anonymous database in MongoDB
4. ## Environmental variables
   - ADMIN - your telegram ID
   - BOT_TOKEN - your telegram bot's API token
   - GROUP - telegram group ID that the bot can send reported message
   - USERNAME - mongodb username
   - PASSWORD - mongodb user password
   - PAYMENT_TOKEN - token to get payments from users

# Future Plans
- *blocking vonstantly reported users*
- *Allowing users to block multiple users at the same time*
- *Automate making premium users without administrator's intervention*
- *Fixing payment procedure*
