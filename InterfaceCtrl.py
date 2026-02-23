from abc import ABC, abstractmethod

class InterfaceCtrl(ABC):
    def __init__(self):
        print("Call InterfaceCtrl::__init__\n")
    
    @abstractmethod
    def open(self) -> None:
        pass
    
    @abstractmethod
    def refresh(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
    
