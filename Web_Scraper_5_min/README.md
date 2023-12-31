**Web Scraping Nifty 50 Stocks with Flask and Selenium**

This project demonstrates how to scrape data from the NSE India website for the top Nifty 50 stocks, display the scraped data on a webpage using Flask, and continuously update the data every 5 minutes using Selenium. The application is designed to mimic human behavior to avoid detection by websites' anti-scraping mechanisms.

**How to Use:**
1. Clone the repository to your local machine.
2. Ensure you have Python and the required dependencies installed. You can install the dependencies using the following command:
   ```
   pip install flask redis beautifulsoup4 pandas selenium
   ```
3. Download the appropriate ChromeDriver executable based on your OS and Chrome version and place it in the project directory.
4. Make sure you have Redis installed and running on your machine, or adjust the Redis connection settings in the `app.py` file if necessary.
5. Modify the `scrape_data` function in `app.py` to customize the URL and data scraping based on your needs.
6. Optionally, adjust the User-Agent and other Selenium options in the `scrape_data` function to mimic human behavior further.
7. Run the Flask application using the following command:
   ```
   python app.py
   ```
8. Access the application in your web browser at `http://127.0.0.1:5000/`. The webpage will display the Nifty 50 stocks and their percentage change values, which will be updated automatically every 5 minutes.

**What It Will Do:**
When the application is executed, it will launch a Flask web server, which will serve a simple webpage showing the top Nifty 50 stocks along with their percentage change values. The data is scraped from the NSE India website using Selenium, and the scraped data is continuously updated every 5 minutes.

The scraping process includes the following steps:
1. The Selenium WebDriver will be started using a headless Chrome browser, configured to mimic human behavior.
2. The WebDriver will navigate to the NSE India website and scroll down the page to load all relevant data.
3. The WebDriver will extract the necessary data from the webpage using BeautifulSoup.
4. The scraped data will be stored in a Redis database and also published to a Redis channel.
5. The Flask application will retrieve the data from Redis and display it on the webpage.
6. The webpage will refresh every 5 minutes to display the updated data.

Please note that web scraping should be done responsibly and in compliance with the terms of service of the website being scraped. Always be considerate of the website's resources and use appropriate delays to avoid overwhelming their servers.
