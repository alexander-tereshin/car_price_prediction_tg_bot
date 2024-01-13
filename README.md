# Car Price Prediction Telegram Bot
Car Price Prediction Bot is a Telegram bot designed to predict car prices based on various parameters. This project was developed as part of the Applied Python course at the Higher School of Economics.

Features
---
* **Single Item Prediction:** Initiate the car price prediction process for a single item.
* **Batch Prediction:** Initiate the car prices prediction process for a batch of items.
* **Rating:** View statistics, including the average rating and usage statistics.
* **Info:** Get information about the bot.
* **Help:** Display the help message.
  
Installation
---
1. Clone the repository:
```bash
$ git clone https://github.com/alexander-tereshin/car_price_prediction_tg_bot.git
```
2. Install virtual enviroment:
```bash
$ cd car_price_prediction_tg_bot/
$ python3 -m venv ./.venv
```
3. Activate virtual enviroment:
```bash
$ source .venv/bin/activate
```
4. Install the required dependencies:
```bash
$ pip install -r requirements.txt
```
5. Create .env and paste your token for bot:
```bash
$ touch .env
```  
Usage
---
Run the bot using the following command:

```bash
$ python main.py
```
Commands
---
* **/start:** Show the welcome message, menu, and restart the bot.
* **/help:** Show the help message and list of commands.
  
Methods
---

- `Single Item Prediction:` Initiate the car price prediction process for a single item. Follow the prompts to provide information about the car.
- `Batch Prediction:` Initiate the car prices prediction process for a batch of items. Upload a CSV file with car entities.
- `Rating:` View statistics, including the average rating and usage statistics.
- `Information:` Get information about the bot.
- `Help:` Display the help message.

License
---
This project is licensed under the terms of the MIT license.
