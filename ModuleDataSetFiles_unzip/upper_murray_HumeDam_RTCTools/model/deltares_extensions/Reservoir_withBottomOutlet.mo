// Used to split the Outflow into Q_bottomoutlet next to the default Q_turbine and
// Q_spill
block Reservoir_withBottomOutlet
  import SI = Modelica.SIunits;
  extends Deltares.ChannelFlow.Internal.QSISO;
  extends Deltares.ChannelFlow.Internal.QForcing;
  extends Deltares.ChannelFlow.Internal.QLateral;

  // Inputs
  input SI.VolumeFlowRate Q_turbine;
  input SI.VolumeFlowRate Q_spill;
  input SI.VolumeFlowRate Q_bottomoutlet;
  // States
  SI.Volume V(min = 0, nominal = 1e6);
equation
  // Mass balance
  der(V) = QIn.Q - QOut.Q + sum(QForcing) + sum(QLateral.Q);
  // Split outflow between turbine and spill flow and bottom outlet
  QOut.Q = Q_turbine + Q_spill + Q_bottomoutlet;
end Reservoir_withBottomOutlet;
