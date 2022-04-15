# play-coin-toss-game
A script that plays the coin-tossing game and determines if the coin is fair.

## Game play:
![alt](https://github.com/ZhongRabbit/play-coin-toss-game/blob/main/src/gameplay.gif)

In order to play this web game, the script needs to:
1. flip the coin 5 times.
2. check how many of the flips so far are heads.
3. compute the math to determine if the coin is likely fair or biased.
4. (if insufficient sample size) add more coin flips!

<br>

## The game:
<img src="https://github.com/ZhongRabbit/play-coin-toss-game/blob/main/src/game_intro.png" alt="game_intro" style="height:600px;"></img>

## The rules:
<img src="https://github.com/ZhongRabbit/play-coin-toss-game/blob/main/src/game_rules.png" alt="game_rules" style="height:600px;"></img>



Note:
1. Since I didn't see a way to check if the coin is fair/biased by examining web elements, the only solution seems to be interact w/ "server-side coin flips" w/ such a script.
2. The numbers of heads and tails are unavailable as raw text, so screen capture and OCR were used to extract these info. OCR via PyTesseract is the bottleneck of the script. It's possible to speed this up by hashing all number images and building a lookup dictionary using pre-computed hashes.
