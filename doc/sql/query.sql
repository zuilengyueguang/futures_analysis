SELECT * FROM vnpy.`dbbardata`;

SELECT * FROM vnpy.`dbtickdata` ORDER BY DATETIME DESC LIMIT 10;

SELECT COUNT(*) FROM vnpy.`dbtickdata`;

SELECT * FROM vnpy.`dbtickdata` WHERE symbol='rb1910' ORDER BY `datetime` DESC;

SELECT * FROM vnpy.`dbtickdata` WHERE DATETIME >= '2019-07-19 09:00:00' AND symbol='SR909';\

SELECT symbol,volume,DATETIME FROM vnpy.`dbtickdata` ORDER BY DATETIME DESC;

SELECT * FROM vnpy.`dbbardata`;
