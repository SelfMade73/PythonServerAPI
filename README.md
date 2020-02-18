# PythonServerAPI
  HTTP server with API 
  
## How to use ##    
*Run it from cmd*  
**python3 script.py**


**From google chrome**  
**http://localhost:8000/api/method?params**  
    
## Methods Description ##

**1) getCityInfoById**  
*returns information about the desired city or displays a message that the identifier was not found*  
*example* : **http://localhost:8000/api/get-city-by-id?id=452838**  
**2) getCitiesByPage**  
*returns information about all cities on required page or displays a message that the parameters is invalid*  
*example* : **http://localhost:8000/api/get-cities-by-page?page=0&per=100**  
**3) pairCitiesInfo**  
*returns information about a pair of cities, their time zone and which one is farther north or displays a message that the parameters are incorrect*    
*example* : **http://localhost:8000/api/get-pair-city?first=Новое%20Село&second=Щипачево**  
**4) getCitiesByStart**  
*returns a list of possible objects that starts with an input parameter*    
*example* : **http://localhost:8000/api/get-objects-by-start?start=Кава**  


