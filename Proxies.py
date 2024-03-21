from multiprocessing.pool import ThreadPool
import os
import threading
import random
import time
import pandas as pd
import requests

from WebAgents import WebAgents
import Constants


class Proxies:

    """Gets proxies from https://geonode.com/free-proxy-list
    """
    def __init__(self) :

        self.previous_subnet = ""
        self.readyProxies= []
        self.proxiesDf=pd.DataFrame()

        self.__downloadProxies()

        

    #region Proxies from API filtering subnet 
 
    def getProxie(self):
        """Gets proxie from filtering the proxie´s subnet  
            Returns: proxy = {
                f'{protocol}' : f'{protocol}://{ip}:{port}',
            }
        """
        
        while True:
            proxie = random.choice(self.readyProxies)
            ip = proxie['ip']
            ip_subnet = ip.split('.')[2]

            #If the subnet is the same, we keep iterating until it´s different
            if ip_subnet != self.previous_subnet:
                self.previous_subnet = ip_subnet
                return proxie
    
    #region Private

    def __downloadProxies(self):
        """Downloads, gives format and test proxies
        """
        apiProxies=[]

        #We get all proxies from the pages selected
        for list in self.__getProxiesFromPage():
            apiProxies= apiProxies + list 

        #And we test them 
        print("Testing proxies...")
        pool=ThreadPool(processes=10)
        pool.map(self.__getWorkingProxies,apiProxies)
        pool.close()
        pool.join()  

        #Then it will create a dataframe  and save it to csv
        self.proxiesDf=pd.DataFrame(self.readyProxies)

        if os.path.exists(Constants.PROXIES_FILENAME):
            os.remove(Constants.PROXIES_FILENAME)

        self.proxiesDf.to_csv(Constants.PROXIES_FILENAME)

    def __getProxiesFromPage(self):
        """Gets proxies from api

        Returns:
            List: proxies list
        """
        print("Downloading proxies...")
        proxiesURls=[]
        pages=Constants.PAGE_NUMBER+1

        #We get the pages, depending on how many are selected in Constants
        for x in range(1,pages):
            proxiesURls.append(f"{Constants.PROXIES_API_SELECT_PAGE}{x}{Constants.PROXIES_API_END}")
        
        pool=ThreadPool(processes=20)
        apiProxies=pool.map(self.__getProxiesFromJson,proxiesURls)
        pool.close()
        pool.join()

        return apiProxies
            
    def __getWorkingProxies(self,apiProxie):
        """Checks which proxies are working and keeps them
        """
        
        ip=apiProxie["ip"]
        port=apiProxie["port"]
        proxy=f"{ip}:{port}"
        protocol=apiProxie["protocols"][0]

        proxy = self.__formatProxie(protocol,ip,port)

        responseTime,working=self.__testProxy(proxy)

        if working:
                self.readyProxies.append({
                    "ip":ip,
                    "proxy": proxy,
                    "protocol":protocol,
                    "response_time": responseTime
                })

    def __getProxiesFromJson(self,url):
        """Returns list with all proxies information, calling an endpoint and returning a json list.

        Returns:
            []: list of proxies
        """

        jsonList=[]

        response=requests.get(url)

        if response.status_code == 200:
            jsonResponse=response.json()['data']

            for i in range(0,len(jsonResponse)):
                jsonList.append(jsonResponse[i]) 
        
        return jsonList  

    def __testProxy(self,proxy):
        """Test proxies giving them user-agents. If they timeout, working = False

        Args:
            proxy (dict): proxy dictionary

        Returns:
            tuple(int,bool): response_time, working
        """
        url = Constants.PROXIE_TEST_URL
        start_time = time.time()

        #We test proxies giving them user-agents. If they timeout, working = False
        try:
            agent=WebAgents()
            headers={'User-Agent': agent.getAgent()}
            response = requests.get(url, proxies=proxy,timeout=10,headers=headers)
            response.raise_for_status()
            response_time = (time.time() - start_time) * 1000

            return response_time, True

        except requests.exceptions.RequestException as e:
            response_time = 0
            return response_time,False

    def __formatProxie(self,protocol,ip,port):
        
        proxy = {}
        if protocol in ["socks4","socks5"]:
            proxy = {
                'socks': f'{protocol}://{ip}:{port}',
            }

        elif protocol in ["http","https"]:
            proxy = {
                f'{protocol}' : f'{protocol}://{ip}:{port}',
            }

        return proxy
    
    #endregion

#endregion

#region Getters / Setters
    
    def get_readyProxies(self):
        return self.readyProxies

    def set_readyProxies(self, value):
        self.readyProxies = value

    def del_elem_readyProxie(self,value):
        self.readyProxies.remove(value)

#endregion

