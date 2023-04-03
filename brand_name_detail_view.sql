SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER VIEW [dbo].[brand_name_detail_mailer] AS
SELECT DISTINCT CAST(time_stamp AS VARCHAR(20)) Date, Platform, 
    COUNT(DISTINCT [location]) [Location Count],
    COUNT(*) AS [Total SKU Count],
    COUNT(CASE WHEN ([status_text] = '' OR [status_text] IS NULL) THEN 1 ELSE NULL END) [Status Blanks],
    COUNT(CASE WHEN [status_text] LIKE '%add%' AND (sp = '' OR sp IS NULL) THEN 1 
        ELSE NULL END) [Price Blanks]
FROM brand_name_detail 
WHERE TRY_CONVERT(DATE, time_stamp, 05) = CAST(GETDATE() AS DATE)
GROUP BY time_stamp, platform

GO
