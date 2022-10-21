import numpy as np
import multiprocessing as mp
from misc.radial import get_function_radius

from algorithm import multi

class SinglePhaseRetriever():
    # TODO: Crea una classe que encapsuli completament el mètode de recuperació de fase
    def __init__(self, *args, **kwargs):
        pass

    def load_dataset(self, path):
        pass

    def seek_central_region(self):
        """Seek the region where the greatest amount of energy is contained."""
        pass
    
    def config(self,):
        pass

class PhaseRetriever(SinglePhaseRetriever):
    # TODO: Deriva un recuperador de fase que utilitzi multiprocessing per a recuperar dues
    # fases a la vegada.
    def __init__(sef, *args, **kwargs):
        super().__init__(*args, **kwargs)
