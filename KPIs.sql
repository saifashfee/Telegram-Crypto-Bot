SELECT * FROM resampled_data
ORDER BY ID;

-- Average Price of Each Coin throughout the day
SELECT [Coin Name], AVG([Last Traded Price($)]) AS [Average Price]
FROM resampled_data
GROUP BY [Coin Name]
ORDER BY [Average Price] DESC;


-- Total Volume traded 
SELECT [Coin Name], SUM([Total Volume]) AS [Total Circulating Volume]
FROM resampled_data
GROUP BY [Coin Name]
ORDER BY [Total Circulating Volume] DESC;


-- Market Cap 
SELECT [Coin Name], MAX([Market Cap ($)]) AS [Highest Market Cap]
FROM resampled_data
GROUP BY [Coin Name]
ORDER BY [Highest Market Cap] DESC;


-- Risk Assessment
SELECT [Coin Name], STDEV([Last Traded Price($)]) AS Volatility
FROM resampled_data
GROUP BY [Coin Name]
ORDER BY Volatility DESC;


-- Price to Volume ratio
SELECT [Coin Name], AVG([Last Traded Price($)]/[Total Volume]) AS [Price to Volume Ratio]
FROM resampled_data
GROUP BY [Coin Name]
ORDER BY [Price to Volume Ratio] DESC;


-- Max Price Change Percentage
SELECT [Coin Name], (MAX([Last Traded Price($)]) - MIN([Last Traded Price($)])) / MIN([Last Traded Price($)]) * 100 AS [Price Change Percentage]
FROM resampled_data
GROUP BY [Coin Name]
ORDER BY [Price Change Percentage] DESC;
