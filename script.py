import socket
import re
import urllib.parse

#Агафонов Алексей Сергеевич СПб

def  createResponseData(responseString : str):
    data: dict = {}
    responseList : list = responseString.split('\t')
    data["geonameid"]  = responseList[0]
    data["name"] = responseList[1]
    data["asciiname"] = responseList[2]
    data["alternatenames"] = responseList[3]
    data["latitude"] = responseList[4]
    data["longitude"] = responseList[5]
    data["feature class"] = responseList[6]
    data["feature code"] = responseList[7]
    data["country code"] = responseList[8]
    data["population"] = responseList[10]
    data["dem"] = responseList[-3]
    data["timezone"] = responseList[-2]
    data["modification date"] = responseList[-1]
    return data

class HTTPserver():


    __HOST:str
    __PORT:int

    __URLS : list = [
                        "/",
                        "/api/get-city-by-id",
                        "/api/get-cities-by-page",
                        "/api/get-pair-city",
                        "/api/get-objects-by-start"
    ]

    def __init__(self,HOST: str ,PORT: int):
        self.__HOST = HOST
        self.__PORT = PORT


    def __parseRequest(self, clientSocket):
        request = clientSocket.recv(4096).decode("utf-8",errors = "ignore").split(" ")
        if (request == ['']):
            return None
        print("Teло запроса : \n" + str(request),end = "\n\n")
        method = request[0]
        URL = request[1]
        return (method,URL)

    def __createHeaders(self, method,url):
        if urllib.parse.urlparse(url).path not in self.__URLS:
            return "HTTP/1.1 404 \n\n",404
        if method != "GET":
            return "HTTP/1.1 405 \n\n",405
        return "HTTP/1.1 200 OK\n\n",200

    def __getContent(self,url:str):
        parsedQuery = urllib.parse.urlparse(url)
        path : str = parsedQuery.path
        params : dict =  urllib.parse.parse_qs(parsedQuery.query)
        if path == self.__URLS[0]:
            response = "START PAGE"
        if path == self.__URLS[1]:
            response = self.getCityInfoById(int(params["id"][0]))
        if path == self.__URLS[2]:
            response = self.getCitiesByPage(int(params["page"][0]),int(params["per"][0]))
        if path == self.__URLS[3]:
            response = self.pairCitiesInfo((params["first"][0]),params["second"][0])
        if path == self.__URLS[4]:
            response = self.getCitiesByStart((params["start"][0]))
        return response
            
    def __serveClient(self, clientSocket):
        request = self.__parseRequest(clientSocket)
        if (request == None):
            return None
        method,url = request
        headers,code = self.__createHeaders(method,url)
        if code == 404:
            return (headers).encode()
        elif code == 405:
            return (headers).encode()
        else:
            content : str = self.__getContent(url)
        return  bytearray(headers.encode("utf-8") + content.encode("utf-16"))

    def __binarySearch(self,itemList:list ,left,right,ID) -> int:
        if right >= left:
            mid = left + (right - left)//2
            if int(itemList[mid].split('\t')[0]) == ID:
                return mid
            elif ID < int(itemList[mid].split('\t')[0]):
                return self.__binarySearch(itemList, left,mid - 1,ID)
            else:
                return self.__binarySearch(itemList,mid + 1,right,ID)
        else:
            return -1

    def pairCitiesInfo(self,fstCity: str, scndCity: str) -> str:
        response: str = "Invalid Parameters"
        allFirstCities: list = []
        allSecondCities: list = []
        north: str = ""
        timezone: str = ""
        with open("RU.txt","r",encoding="utf-8") as db:
            allLines: list = db.readlines()
        for line in allLines :
            if re.search(","+fstCity,line):
                allFirstCities.append(line)
            elif re.search(","+scndCity + "\t",line):
                allSecondCities.append(line)
        if len(allFirstCities) == 0 or len(allSecondCities) == 0:
            return response
        if len(allFirstCities) > 1:
            for i in range(len(allFirstCities)):
                allFirstCities[i] = createResponseData(allFirstCities[i])
            oneFirstCity = max(allFirstCities,key=lambda parameter_list: int(parameter_list["population"]))
        else:
            oneFirstCity = createResponseData(allFirstCities[0])
        if len(allSecondCities) > 1:
            for i in range(len(allSecondCities)):
                allSecondCities[i] = createResponseData(allSecondCities[i])
            oneSecondCity = max(allSecondCities,key=lambda parameter_list: int(parameter_list["population"]))
        else:
            oneSecondCity = createResponseData(allSecondCities[0])
        if float(oneFirstCity["latitude"]) > float(oneSecondCity["latitude"]):
            north = "Первый географический объект севернее"
        elif float(oneFirstCity["latitude"]) < float(oneSecondCity["latitude"]):
            north = "Второй географический объект севернее"
        else:
            north = "Объекты на одной широте"
        if oneFirstCity["timezone"] == oneSecondCity["timezone"]:
            timezone =  "Объекты находятся в одном часовом поясе: {}".format(oneFirstCity["timezone"])
        else:
            timezone =  "Объекты находятся в  разных часовых поясах"
        response = ("ИНФОРМАЦИЯ О ПЕРВОМ ОБЪЕКТЕ {} \n\n\n"\
        "ИНФОРМАЦИЯ О ВТОРОМ ОБЪЕКТЕ {}\n\n\n{}\n\n\n{}").format(str(oneFirstCity),
                                                                str(oneSecondCity),
                                                                north,
                                                                timezone)
        return response

    def getCityInfoById(self,ID: int) -> str:
        with open("RU.txt","r",encoding="utf-8") as db:
            allLines = db.readlines()
        index = self.__binarySearch(allLines,0,len(allLines),ID)
        if (index != -1):
            return str(createResponseData(allLines[index]))
        return "Id was not found"

    def getCitiesByPage(self, page , itemsPerPage) -> str:
        with open("RU.txt","r",encoding="utf-8") as db:
            allLines = db.readlines()
        try:
            if ((itemsPerPage > len(allLines)) or( itemsPerPage < 1) or
             (page < 0) or (page > (len(allLines)//itemsPerPage + 1))):
                raise AssertionError
        except AssertionError:
            return "Invalid parameters..."
        response: str = ""
        for item in allLines[page*itemsPerPage:(page+1)*itemsPerPage]:
            response += (str(createResponseData(item)) + "\n\n\n")
        return response

    def getCitiesByStart(self,begining:str):
        with open("RU.txt","r",encoding="utf-8") as db:
            allLines = db.readlines()
        objectNames:set  = set()
        for line in allLines:
            mainName = line.split('\t')[1]
            asciiName = line.split('\t')[2]
            alternateNames = line.split('\t')[3].split(',')
            for i in alternateNames :
                if re.match(begining,i):
                    objectNames.add(i)
            if re.match(begining,asciiName):
                objectNames.add(asciiName)
            if re.match(begining,mainName):
                objectNames.add(mainName)
        return "Возможно Вы имелли в виду " + str(objectNames)


    def server_start(self):
        serverSocket : socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM,proto=0)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((self.__HOST,self.__PORT))
        serverSocket.listen()
        while True:
                clientSocket , _ =  serverSocket.accept()
                response  = self.__serveClient(clientSocket)
                if response == None:
                    continue
                clientSocket.sendall(response)
                clientSocket.close()
        




if __name__ == '__main__':
    
    http = HTTPserver("127.0.0.1",8000)
    http.server_start()
