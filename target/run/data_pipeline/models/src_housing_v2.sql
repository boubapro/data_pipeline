
  
    

create or replace table SNOWFLAKE_LEARNING_DB.PUBLIC.src_housing_v2
    
    
    
    as (

SELECT *
FROM SNOWFLAKE_LEARNING_DB.PUBLIC.src_housing
where c10='maille'
    )
;


  