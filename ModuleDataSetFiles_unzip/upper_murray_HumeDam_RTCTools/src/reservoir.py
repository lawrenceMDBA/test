import numpy as np

from typing import List, Union

class Reservoir():

    def __init__(self, name, vh_data, reservoir_properties):
        self.__vh_lookup = vh_data
        self.name = name
        self.properties = reservoir_properties

    def level_to_volume(self, levels: Union[float, np.ndarray]):
        return np.interp(levels, self.__vh_lookup['Elevation_m'], self.__vh_lookup['Storage_m3'])

    def volume_to_level(self, volumes: Union[float, np.ndarray]):
        return np.interp(volumes, self.__vh_lookup['Storage_m3'], self.__vh_lookup['Elevation_m'])

    def set_Vsetpoints(self):
        # define interpolated volume setpoints corresponding to heights used in goals:
        self.Vsetpoints = {}

        self.Vsetpoints['surcharge'] = self.level_to_volume(self.properties['surcharge'])
        self.Vsetpoints['fullsupply'] = self.level_to_volume(self.properties['fullsupply'])
        self.Vsetpoints['crestheight'] = self.level_to_volume(self.properties['crestheight'])


class Delay():
    def __init__(self, name, delay_properties):
        self.name = name
        self.delay = delay_properties[0]
