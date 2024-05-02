# pokemon-showdown-ai-cs4804-sp24-group15

Pokemon Showdown UI cloned from smogon's pokemon showdown git repository.\
Code inspired by poke-env and RemptonGames

Our AI application is located in ./bot/Minimax.py\
Minimax.py is where our minimax with alpha-beta pruning is implemented. In this file, along with the algorithm, we also create another bot that simply prioritizes Max Damage Moves. In our main function in Minimax.py, we create two bots, one for our algorithm and one for either a random bot or max damage bot, and run n battles against each other.\
GameState.py represents each game state of our game tree. This is where we also generate child state nodes for each pokemon move/switch.\
BattleUtilities.py represents our utility functions for calculating damage, total HP, physical and special ratios, speed calculations, and type multipliers.

Steps to run bot:
1. Run pokemon showdown server locally:

npm install\
cp config/config-example.js config/config.js\
node pokemon-showdown start --no-security

2. Run Minimax bot:

cd bot\
Change main function in Minimax.py if you want to change between Max Damage Player or Random Player, and number of battles to run.\
python Minimax.py

3. You can then go to your localhost with port 8000 to see each of the battles.
