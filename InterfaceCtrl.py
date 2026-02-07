from abc import ABC, abstractmethod

class InterfaceCtrl(ABC):
    def __init__(self):
        print("Call InterfaceCtrl::__init__\n")
    
    @abstractmethod
    def open(self):
        pass
    
    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def close(self):
        pass
    
