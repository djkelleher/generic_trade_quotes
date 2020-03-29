## Description
The [Generic Trade web interface](https://www.generictrade.com/) requires manually refreshing the page to load new quote data. This script is a workaround to get a continuous data stream from the web interface.

## Configuration
Set your account number and password to the
'account_number' and 'password' fields in the cfg.py file.
If you are not using a demo account, change the 'account_domain' to the domain of your account.
Data can be streamed through a simple HTTP client, but a browser must first be used to log in and get a cookie. Either make a call to quotes.get_cookie or login via your browser and copy/paste the cookie from the browser's dev tools. The cookie should have fields CertigoTZ and CertigoSID.