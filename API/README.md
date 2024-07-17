# The new design layout:

## Endpoints

alot of the endpoints are pointless and are just wrapper of telegrm api methods without adding anything substantial to them.
Insted of these of these enpoints whenever I will need to use this functions I will use the bot_actions function insted of using a redundant endpoint.

delete sendMedia enpoint and only use the bot_action function for it and as for the getUpdates I lean on delete the rest are not redundant

## tests redesign

there needs to two main folders in the tests dir one for the endpoints and the other one for the bot_actions than each function and endpoint or atleast each group of functions in the case for bot_actions get their own dedicated tests. not much code needed here just some moving around the written code
