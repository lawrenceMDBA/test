from rtctools.simulation.pi_mixin import PIMixin
from rtctools.simulation.simulation_problem import SimulationProblem
from rtctools.util import run_simulation_problem

import pandas as pd
from collections import deque
import reservoir
import logging
from typing import List, Union

logger = logging.getLogger("rtctools")
     
class ReservoirModel__simulation(PIMixin, SimulationProblem):

    def __init__(self, *args, reservoirs_csv_path: str, volume_level_csv_paths: List[str], delays_csv_path: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.__debug = False
        # processing reservoir data
        res_df = pd.read_csv(reservoirs_csv_path, sep=";", index_col=0)
        vh_data = []

        for vh_data_file in volume_level_csv_paths:
            vh_data.append(pd.read_csv(vh_data_file, sep=";", index_col=0))
            vh_data_df = pd.concat(vh_data)

        self.reservoirs = {}

        for index, row in res_df.iterrows():
            self.reservoirs[index] = reservoir.Reservoir(index, vh_data_df.loc[index], row)
            self.reservoirs[index].set_Vsetpoints()

        delays_df = pd.read_csv(delays_csv_path, sep =";", index_col=0)
        self.delays = {}
        for index, row in delays_df.iterrows():
            self.delays[index] = reservoir.Delay(index, row)


    def initialize(self):
            # computation of volume corresponding to crestheight:
        for res in self.reservoirs:
            self.set_timeseries("{}_V".format(self.reservoirs[res].name),
                                    self.get_timeseries("{}_V_init".format(self.reservoirs[res].name)))
            self.set_timeseries("{}_Qspill".format(self.reservoirs[res].name),
                                    self.get_timeseries("{}_Qspill_init".format(self.reservoirs[res].name)))
            self.set_timeseries("{}_Qturbine".format(self.reservoirs[res].name),
                                    self.get_timeseries("{}_Qturbine_init".format(self.reservoirs[res].name)))
            self.set_timeseries("{}_Qbottomoutlet".format(self.reservoirs[res].name),
                                self.get_timeseries("{}_Qspill_init".format(self.reservoirs[res].name)))


        self.my_delayed_signals = {}
        for name in self.delays:
            self.my_delayed_signals[name] = deque(list(self.get_timeseries("{}_Q_delayed".format(name))[0:int(self.delays[name].delay)]))

        super().initialize()

    def get_output_variables(self):
        output_variables = super().get_output_variables().copy()

        for res in self.reservoirs:
            output_variables.extend(['{}_V'.format(res), '{}_Qspill'.format(res),
                                   '{}_Qturbine'.format(res), '{}_Qbottomoutlet'.format(res)])
        return output_variables

    def update(self, dt):

        if dt < 0:
            dt = self._PIMixin__dt
        newtime = self.get_current_time() + dt
        print("*** Simulation time:", self._PIMixin__sec_to_datetime(newtime), " ***")

        for res in self.reservoirs:
            # physical limits
            _Qturbine_max = self.reservoirs[res].properties['q_turbine_max']
            _Qspill_max = self.reservoirs[res].properties['q_spill_max']
            _Qbottomoutlet_max = self.reservoirs[res].properties['q_bottomoutlet_max']
            # the user-defined total release
            _Q_user = self.timeseries_at('{}_ReleaseRealtime'.format(res), newtime)
            # the portion that goes through the turbine
            _Q_turbine = min(_Qturbine_max,_Q_user)
            # the portion that goes through the lower valves
            _Q_bottomoutlet = min(_Qbottomoutlet_max,(_Q_user - _Q_turbine))
            # the portion that goes through the spillway depends on the crestheight.
            if self.get_var("{}_V".format(res))> self.reservoirs[res].Vsetpoints['crestheight']:
                _Q_spill = min(_Qspill_max, (_Q_user - _Q_turbine - _Q_bottomoutlet))
            else:
                _Q_spill = 0
            # the remainder must stay in the reservoir.
            _Q_remainder = _Q_user - _Q_turbine - _Q_bottomoutlet - _Q_spill
            logging.debug("_Q_user: {}, _Q_turbine: {}, _Q_bottomoutlet: {}, _Q_spill: {}, _Q_remainder: {}".format(
                _Q_user, _Q_turbine, _Q_bottomoutlet, _Q_spill, _Q_remainder))

            # assign the values to the time series
            self.set_var('{}_Qturbine'.format(res), _Q_turbine)
            self.set_var('{}_Qbottomoutlet'.format(res), _Q_bottomoutlet)
            self.set_var('{}_Qspill'.format(res), _Q_spill)
            # Qout is calculated by Modelica in the Reservoir_withBottomOutlet class


        # pop signal after delay into the correct Q_delay
        for k, v in self.my_delayed_signals.items():
            self.set_var(f'{k}.Q_delayed', self.my_delayed_signals[k].popleft())
        # move one time step forward (dt)
        super().update(dt)
        # load newly computed values into memory to be delayed
        for k, v in self.my_delayed_signals.items():
            self.my_delayed_signals[k].append(self.get_var(f'{k}.QIn.Q'))

    def post(self):
        # compute water levels from computed volume
        results = self.extract_results()
        for res in self.reservoirs:
            result_H = self.reservoirs[res].volume_to_level(results['{}_V'.format(res)])
            self.set_timeseries('{}_H'.format(res), result_H)
        # End of water level computation
        logging.info("End of Simulation run")
        super().post()

        super().post()
        if self.__debug == True:
            # translate xml output file to a csv file
            import pandas4RTC
            pandas4RTC.main()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='RTC_Tools reservoir simulation input arguments.')
    parser.add_argument('--reservoirs_csv_path', help='Path to csv file with reservoir-properties \
    (default: "./model/reservoirs.csv")', default=r"./model/reservoirs.csv", nargs='+')
    parser.add_argument('--volume_level_csv_paths', help='List of path to csv files with reservoir volume-level tables \
    (default: "./model/volumelevel.csv")', default=r"./model/volumelevel.csv", nargs='+')
    parser.add_argument('--delays_csv_path', help='Path to csv file with delay-properties \
    (default: "./model/delays.csv")', default=r"./model/delays.csv", nargs='+')

    args = parser.parse_args()
    reservoirs_csv_path = args.reservoirs_csv_path
    volume_level_csv_paths = args.volume_level_csv_paths
    delays_csv_path = args.delays_csv_path

    run_simulation_problem(ReservoirModel__simulation, reservoirs_csv_path=reservoirs_csv_path[0], \
                             volume_level_csv_paths=volume_level_csv_paths, delays_csv_path=delays_csv_path[0])
