# Mercado-Livre-Price-Tracker-
An application to track the price of products similar to the ones the user is selling.

This app gets the products the user is selling and tracks the price of similar products sold by other people/stores. It gets only the first 50 (if it has that many) results for each product, but this can be increased if a for loop is applied over all pages of results obtained in the search step (changing the offset as explained in the Mercado Livre Api page -> https://developers.mercadolivre.com.br/pt_br/api-docs-pt-br). I made the algorithm search for products that were in same category from the user's product category and return only the products sold by power_sellers. These options can be changed in the 'payload_seach' variable to any kind of filter the user wants (the available filters are listed in the api page) and I used the two I mentioned just to reduce the results from each search.
A json file is generated with the user's product and the similar products found previously.
After this the app will use the Trello API and update (or create) the "ML_Board" of the user with the information stored in the json file. A "Previous Board" is also used to store values obtained previously, so the user can compare them and see if there were any changes in the tracked products.
This application runs 24/7, and it updates the json file and trello board every 5 hours.

I am not providing my app key so, if you want to test it, create a mercado livre account and ask for developer's access (https://developers.mercadolivre.com.br/).


A problem that has to be looked at: The search of similar products also return some products that are not that similar to our product, but we might end up with no results if we use an overly specific term in the search step. This might be solved using some Machine Learning Algorithm (KNN or K-means, for example) and implemented before the search step in this application.

