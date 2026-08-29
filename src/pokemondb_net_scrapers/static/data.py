from pokemondb_net_scrapers.classes.dlc import Dlc
from ..classes.dex import Dex
from ..classes.game import Game

dexes = [
	Dex(1,"red-blue-yellow","Red/Blue/Yellow","Red, Blue & Yellow",1),
	Dex(2,"gold-silver-crystal","Gold/Silver/Crystal","Gold, Silver & Crystal",2),
	Dex(3,"ruby-sapphire-emerald","Ruby/Sapphire/Emerald","Ruby, Sapphire & Emerald",3),
	Dex(4,"firered-leafgreen","FireRed/LeafGreen","FireRed & LeafGreen",3),
	Dex(5,"diamond-pearl","Diamond/Pearl","Diamond & Pearl",4),
	Dex(6,"platinum","Platinum","Platinum",4),
	Dex(7,"heartgold-soulsilver","HeartGold/SoulSilver","HeartGold & SoulSilver",4),
	Dex(8,"black-white","Black/White","Black & White",5),
	Dex(9,"black-white-2","Black 2/White 2","Black 2 & White 2",5),
	Dex(10,"x-y","X/Y","X & Y",6),
	Dex(11,"omega-ruby-alpha-sapphire","Omega Ruby/Alpha Sapphire","Omega Ruby & Alpha Sapphire",6),
	Dex(12,"sun-moon","Sun/Moon","Sun & Moon",7),
	Dex(13,"ultra-sun-ultra-moon","Ultra Sun/Ultra Moon","Ultra Sun & Ultra Moon",7),
	Dex(14,"lets-go-pikachu-eevee","Let's Go Pikachu/Let's Go Eevee","Let's Go Pikachu & Let's Go Eevee",7),
	Dex(15,"sword-shield","Sword/Shield","Sword & Shield",8),
	Dex(16,"brilliant-diamond-shining-pearl","Brilliant Diamond/Shining Pearl","Brilliant Diamond & Shining Pearl",8)
]

games = [
    Game(1, 1,"Red","red",["Kanto"]),
    Game(2, 1,"Blue","blue",["Kanto"]),
    Game(3, 1,"Yellow","yellow",["Kanto"]),
    Game(4, 2,"Gold","gold",["Kanto","Johto"]),
    Game(5, 2,"Silver","silver",["Kanto","Johto"]),
    Game(6, 2,"Crystal","crystal",["Kanto","Johto"]),
    Game(7, 3,"Ruby","ruby",["Hoenn"]),
    Game(8, 3,"Sapphire","sapphire",["Hoenn"]),
    Game(9, 3,"Emerald","emerald",["Hoenn"]),
    Game(10, 4,"FireRed","firered",["Kanto"]),
    Game(11, 4,"LeafGreen","leafgreen",["Kanto"]),
    Game(12, 5,"Diamond","diamond",["Sinnoh"]),
    Game(13, 5,"Pearl","pearl",["Sinnoh"]),
    Game(14, 6,"Platinum","platinum",["Sinnoh"]),
    Game(15, 7,"HeartGold","heartgold",["Kanto","Johto","Hoenn","Sinnoh"]),
    Game(16, 7,"SoulSilver","soulsilver",["Kanto","Johto","Hoenn","Sinnoh"]),
    Game(17, 8,"Black","black",["Unova"]),
    Game(18, 8,"White","white",["Unova"]),
    Game(19, 9,"Black 2","black2",["Unova"]),
    Game(20, 9,"White 2","white2",["Unova"]),
    Game(21, 10,"X","x",["Kalos"]),
    Game(22, 10,"Y","y",["Kalos"]),
    Game(23, 11,"Omega Ruby","omega-ruby",["Hoenn"]),
    Game(24, 11,"Alpha Sapphire","alpha-sapphire",["Hoenn"]),
    Game(25, 12,"Sun","sun",["Alola"]),
    Game(26, 12,"Moon","moon",["Alola"]),
    Game(27, 13,"Ultra Sun","ultra-sun",["Alola"]),
    Game(28, 13,"Ultra Moon","ultra-moon",["Alola"]),
    Game(29, 14,"Let's Go Pikachu","lets-go-pikachu",["Kanto"]),
    Game(30, 14,"Let's Go Eevee","lets-go-eevee",["Kanto"]),
    Game(31, 15,"Sword","sword",["Galar"]),
    Game(32, 15,"Shield","shield",["Galar"]),
	Game(33, 16,"Brilliant Diamond","brilliant-diamond",["Sinnoh"]),
	Game(34, 16,"Shining Pearl","shining-pearl",["Sinnoh"])
]

dlcs = [
    Dlc(1, 15, "The Isle of Armor", "isle-of-armor"),
    Dlc(2, 15, "The Crown Tundra", "crown-tundra")
]