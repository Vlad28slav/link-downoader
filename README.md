In order to work this repository needs an .env file to store dpopbox app token. More info here: https://developers.dropbox.com/oauth-guide
This application saves your file and you receive a link( works only for localhost now unfortunatly). So anyone who has the link can download your file, as long as there is no password.
You can set a password to file(it is optional), so the application will not give file untill user's provided password would not passed.
There are 8 options of time awaliability for link, up to 8 hours, after that file will be deleteted from database.
Since i used free dpobpox account as a base, the limit is 2 GB per account, so do not overload this limit, the limit is for all files total, not per file 
