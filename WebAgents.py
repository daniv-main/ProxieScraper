from functools import lru_cache
import random

import Constants

class WebAgents:
    """Gets random web agents to use as headers
    """
    def __init__(self) -> None:
        self.cache=self.__readAgents()

    def getAgent(self):
        """Returns random agent

        Returns:
            str: agent
        """
        return self.cache[random.randint(1, 999)]

    def __readAgents(self):
        """Loads user agents from file

        Returns:
            []: 1000 user agents
        """
        webAgents=[]

        with open(f"{Constants.WEB_AGENTS}", "r") as f:
            lines = f.readlines()
            webAgents=[line.strip() for line in lines]  # Remove leading/trailing whitespace

        return webAgents

 


