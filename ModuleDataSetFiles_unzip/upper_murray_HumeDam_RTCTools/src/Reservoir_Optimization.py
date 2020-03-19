from rtctools.optimization.collocated_integrated_optimization_problem \
    import CollocatedIntegratedOptimizationProblem
from rtctools.optimization.goal_programming_mixin \
    import GoalProgrammingMixin, Goal, StateGoal
from rtctools.optimization.modelica_mixin import ModelicaMixin
from rtctools.optimization.pi_mixin import PIMixin
from rtctools.util import run_optimization_problem
from rtctools.optimization.timeseries import Timeseries
import reservoir
import os
import logging

import numpy as np
import pandas as pd

from typing import List, Union

logger = logging.getLogger("rtctools")

class StateRangeGoal(StateGoal):
    """
    A state goal applies for each state variable and each time step.
    This goal is used to try to keep the state variable in the target range.
    """
    def __init__(self, optimization_problem, priority, variable, target_min=0, target_max=0, weight=1., function_nominal=1.):
        self.target_min = target_min
        self.target_max = target_max
        self.state = variable
        self.priority = priority
        self.weight = weight
            # function range is loaded from the bounds set in modelica
        self.function_range = optimization_problem.bounds()[variable]
        self.function_nominal = function_nominal
    # The penalty variable is taken to the order'th power.
    order = 1


class StateMinimizationGoal(StateGoal):
    """
    A state goal applies for each state variable and each time step.
    This goal is used to minimize the state variable.
    """
    def __init__(self, priority, variable, weight=1., function_nominal=1.):
        self.state = variable
        self.priority = priority
        self.weight = weight
        self.function_nominal=function_nominal
    # The penalty variable is taken to the order'th power.
    order = 1


class SmoothQTurbine(StateGoal):
    """
        A state goal applies for each state variable and each time step.
        This goal is used in combination with the last two constraints to minimize the
        absolute value of the derivative of 'ReservoirHume_Qturbine'
    """
    def __init__(self, priority, location, weight=1., function_nominal=1.):
        self.state = '{}_absQturbder'.format(location)
        self.priority = priority
        self.weight = weight
        self.function_nominal = function_nominal

    order = 1


class ReservoirModel(GoalProgrammingMixin, PIMixin,
                         ModelicaMixin, CollocatedIntegratedOptimizationProblem):

    def __init__(self, *args, reservoirs_csv_path: str, volume_level_csv_paths: List[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.__debug = False

        res_df = pd.read_csv(reservoirs_csv_path, sep=";", index_col=0)
        vh_data = []

        for vh_data_file in volume_level_csv_paths:
            vh_data.append(pd.read_csv(vh_data_file, sep=";", index_col=0))
            vh_data_df = pd.concat(vh_data)

        self.reservoirs = {}

        for index, row in res_df.iterrows():
            self.reservoirs[index] = reservoir.Reservoir(index, vh_data_df.loc[index], row)
            self.reservoirs[index].set_Vsetpoints()



    def pre(self):
        # preprocessing is used to process some data before optimization is started.
        super().pre()

        for i in self.reservoirs:
            self.set_timeseries("{}_V".format(self.reservoirs[i].name), self.get_timeseries("{}_V_init".format(self.reservoirs[i].name)))


    def path_goals(self):
        # path goals apply for each time step individually
        def _append_goals(g, name):

            if self.parameters(0).get("{}_use_surcharge_max".format(name), True):
                _priority = self.parameters(0).get("{}_priority_surcharge_max".format(name), 4)
                g.append(StateRangeGoal(self, _priority, '{}_V'.format(name), target_min=2e9,
                                        target_max=self.reservoirs[name].Vsetpoints['surcharge'], function_nominal=1e9))

            # further reduce maximum reservoir volume to full supply level, if possible
            if self.parameters(0).get("{}_use_fullsupply_max".format(name), False):
                _priority = self.parameters(0).get("{}_priority_fullsupply_max".format(name), 8)
                g.append(StateRangeGoal(self, _priority, '{}_V'.format(name), target_min=2e9,
                                        target_max=self.reservoirs[name].Vsetpoints['fullsupply'], function_nominal=1e9))

            # Discharge at downstream location for low flow and high flow
            if self.parameters(0).get("{}_use_downstreamflow_target_range".format(name), False):
                _priority = self.parameters(0).get("{}_priority_downstreamflow_target_range".format(name), 11)
                if self.reservoirs[name].properties['lowflowlocation'] == np.nan:
                    g.append(StateRangeGoal(self, _priority, '{}_Q'.format(self.reservoirs[name].properties['lowflowlocation']),
                                            self.parameters(0).get("{}_downstreamflow_target_min".format(name)),
                                            self.parameters(0).get("{}_downstreamflow_target_max".format(name))))
                else:
                    logging.warning('No downstream target location specified in reservoir-properties file for {}. Skipping downstream flow target goal.'.format(name))

             # apply user defined release scheme, if possible
            if self.parameters(0).get("{}_use_track_release_timeseries".format(name), True):
                _priority = self.parameters(0).get("{}_priority_track_release_timeseries".format(name), 10)
                g.append(StateRangeGoal(self, _priority, '{}_Qout'.format(name),
                                        self.get_timeseries('{}_ReleaseRealtime'.format(name)),
                                        self.get_timeseries('{}_ReleaseRealtime'.format(name))))

            # this goal can be used in draught situations to minimize the total release of water (useful when 'ReleaseRealtime' is not used as target)
            if self.parameters(0).get("{}_use_minimize_Qout".format(name), True):
                _priority = self.parameters(0).get("{}_priority_minimize_Qout".format(name), 10)
                g.append(StateMinimizationGoal(_priority, '{}_Qout'.format(name), function_nominal=1e3))

            # Minimization goal of reservoir release via Q_spill
            if self.parameters(0).get("{}_use_minimize_Qspill".format(name), True):
                _priority = self.parameters(0).get("{}_priority_minimize_Qspill".format(name), 12)
                g.append(StateMinimizationGoal(_priority, '{}_Qspill'.format(name), function_nominal=1e3))

            # this goal is used to smoothen operation of the turbine over time (and generally given the last priority)
            if self.parameters(0).get("{}_use_smoothen_Qturbine".format(name), True):
                _priority = self.parameters(0).get("{}_priority_smoothen_Qturbine".format(name), 100)
                g.append(SmoothQTurbine(_priority, name))
            return g

        g = super().path_goals()

        for res in self.reservoirs:
            previous_nrgoals = len(g)
            g = _append_goals(g, res)
            logger.info('Reservoir: {}, Number of goals added: {} for reservoir '.format(res, len(g)- previous_nrgoals))
        return g


    def path_constraints(self, ensemble_member):
        # constraints
        def _append_constraints(c, name):
            # set volume constraints
            __v_init = self.get_timeseries("{}_V_init".format(self.reservoirs[name].name)).values[0]
            __v_max = self.reservoirs[name].properties['volume_max']
            __v_min = self.reservoirs[name].properties['volume_min']
            if __v_init > __v_max:
                logger.error('V_init {} > V_max {}, reservoir {}'.format(__v_init, __v_max, name))
            if __v_init < __v_min:
                logger.error('V_init {} < V_min {}, reservoir {}'.format(__v_init, __v_max, name))
            c.append((self.state('{}_V'.format(name)), __v_min, __v_max))

            # Constraint for the capacity of the turbines (physical min and max)
            # broad estimate using P=eta*rho*g*h*Q
            c.append((self.state('{}_Qturbine'.format(name)), 0, float(self.reservoirs[name].properties['q_turbine_max'])))
            # capacity of Q_spill
            c.append((self.state('{}_Qspill'.format(name)), 0, float(self.reservoirs[name].properties['q_spill_max'])))
            # constraints used to minimize the absolute value of the Qturb derivative
            c.append((self.state('{}_absQturbder'.format(name)) - self.der('{}_Qturbine'.format(name)), 0.0,
                      np.inf))
            c.append((self.state('{}_absQturbder'.format(name)) + self.der('{}_Qturbine'.format(name)), 0.0,
                      np.inf))
            return c
        constraints = super(ReservoirModel, self).path_constraints(ensemble_member)

        for res in self.reservoirs:
            constraints = _append_constraints(constraints, res)

        if self.__debug == True:
            self._write_goals_to_csv()
        return constraints

# post processing
    def post(self):
        # postprocessing is used to process some data after optimization has ended.
        # compute water levels from computed volume
        results = self.extract_results()
        for res in self.reservoirs:
            result_H = self.reservoirs[res].volume_to_level(results['{}_V'.format(res)])
            self.set_timeseries('{}_H'.format(res), result_H)
        # End of water level computation
        logging.info("Completed optimization run successfully")
        super().post()
            # translate xml file to a csv file
        if self.__debug == True:
            import pandas4RTC
            pandas4RTC.main()

    def solver_options(self):
        options = super().solver_options()
        solver = options['solver']
        options['expand'] = True
        if args.solver == 'clp':
            options['solver'] = 'clp'
            options['casadi_solver'] = 'qpsol'
        elif args.solver == 'cplex':
            options['solver'] = 'cplex'
            options['casadi_solver'] = 'qpsol'
            cplex = options['cplex'] = {}
            cplex['CPXPARAM_Read_Scale'] = -1
            cplex['CPX_PARAM_EPOPT'] = 1e-8  # optimality tolerance
        else:   # opopt
            options[solver]['jac_c_constant'] = 'yes'  # equality constraints are linear
            options[solver]['jac_d_constant'] = 'yes'  # inequality constraints are linear
            options[solver]['hessian_constant'] = 'yes'  # nonlinearities (in objective) are at most quadratic

        return options

    def _write_goals_to_csv(self):
        logger.debug("Writing goals for debugging purpose.")
        fname = './debug/goal_output.csv'
        if not os.path.exists(os.path.dirname(fname)):
            os.makedirs(os.path.dirname(fname))
        try:
            o = open(fname, 'w')
        except IOError:
            logger.error('Could not open {}. File locked, no goals written for debug purposes '.format(fname))
        else:
            o.write(
                'goal_type;priority;state;target_min;target_max;frange_min;frange_max;fnominal;\n')
            for g in self.path_goals() + self.goals():
                _min = g.target_min
                _frange_min = g.function_range[0]

                if isinstance(_min, Timeseries):
                    _min = np.min(_min.values)  # Instead of writing the full array, we pick the extreme value.
                elif isinstance(_min, np.ndarray):
                        _min = np.min(_min)  # Instead of writing the full array, we pick the extreme value.
                elif np.isnan(_min):
                    _min = ''
                _max = g.target_max
                _frange_max = g.function_range[1]
                _function_nominal = g.function_nominal
                if isinstance(_max, Timeseries):
                    _max = np.max(_max.values)  # Instead of writing the full array, we pick the extreme value.
                elif isinstance(_max, np.ndarray):
                        _max = np.max(_max)  # Instead of writing the full array, we pick the extreme value.
                elif np.isnan(_max):
                    _max = ''

                o.write('{cname};{priority};{state};{_min};{_max};{_frange_min};{_frange_max};'
                        '{_function_nominal};\n'.format(
                    cname=g.__class__.__name__,
                    _min=_min,
                    _max=_max,
                    _frange_min=_frange_min,
                    _frange_max=_frange_max,
                    _function_nominal=_function_nominal,
                    **g.__dict__))
            o.close()

        _bounds = self.bounds()

        fname = './debug/bounds_output.csv'
        if not os.path.exists(os.path.dirname(fname)):
            os.makedirs(os.path.dirname(fname))
        try:
            o = open(fname, 'w')
        except IOError:
            logger.error('Could not open {}. File locked, no bounds written for debug purposes '.format(fname))
        else:
            for k, (m, M) in _bounds.items():
                o.write("{};{};{}\n".format(k, m, M))
            o.close()
# Run

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='RTC_Tools reservoir optimization input arguments.')
    parser.add_argument('--reservoirs_csv_path', help='Path to csv file with reservoir-properties \
    (default: "./model/reservoirs.csv")', default=r"./model/reservoirs.csv", nargs='+')
    parser.add_argument('--volume_level_csv_paths', help='List of path to csv files with reservoir volume-level tables \
    (default: "./model/volumelevel.csv")', default=r"./model/volumelevel.csv", nargs='+')
    parser.add_argument('--solver', help='option to choose solver clp (default) or ipopt as solver', default='clp')

    args = parser.parse_args()
    reservoirs_csv_path = args.reservoirs_csv_path
    volume_level_csv_paths = args.volume_level_csv_paths
    preferred_solver = args.solver
    run_optimization_problem(ReservoirModel, reservoirs_csv_path=reservoirs_csv_path[0], \
                             volume_level_csv_paths=volume_level_csv_paths, preferred_solver=preferred_solver)
