model ReservoirModel__simulation
  import SI = Modelica.SIunits;
  // Schematization elements
  Reservoir_withBottomOutlet ReservoirHume annotation(
    Placement(visible = true, transformation(origin = {-42, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.SimpleRouting.BoundaryConditions.Inflow InflowHume annotation(
    Placement(visible = true, transformation(origin = {-80, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  FixedDelay MurrayRiver1 annotation(
    Placement(visible = true, transformation(origin = {-2, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.SimpleRouting.Nodes.Node KiewaInflow (nin = 2, nout = 1) annotation(Placement(visible = true, transformation(origin = {28, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.SimpleRouting.BoundaryConditions.Terminal TerminalDoctorsPoint annotation(
    Placement(visible = true, transformation(origin = {88, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  FixedDelay MurrayRiver2 annotation(
    Placement(visible = true, transformation(origin = {62, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));  
  FixedDelay Tributary annotation(
    Placement(visible = true, transformation(origin = {20, 52}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Deltares.ChannelFlow.SimpleRouting.BoundaryConditions.Inflow InflowTributary annotation(
    Placement(visible = true, transformation(origin = {20, 82}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  // Time series
  input SI.VolumeFlowRate ReservoirHume_Inflow_Q(fixed = true);
  input SI.VolumeFlowRate Tributary_Inflow_Q(fixed = true);
  input SI.VolumeFlowRate ReservoirHume_Qturbine(fixed = false);
  input SI.VolumeFlowRate ReservoirHume_Qspill(fixed = false);
  input SI.VolumeFlowRate ReservoirHume_Qbottomoutlet(fixed = false);
  input SI.VolumeFlowRate MurrayRiver1_Q_delayed(fixed = true);
  input SI.VolumeFlowRate MurrayRiver2_Q_delayed(fixed = true);
  input SI.VolumeFlowRate Tributary_Q_delayed(fixed = true);
  output SI.Volume  ReservoirHume_V(min = 10^9, max = 10^11);
  output SI.VolumeFlowRate ReservoirHume_Qout(min = 0, max = 2*10^3);
  output SI.VolumeFlowRate DoctorsPoint_Q(min = 0, max = 10^3);
  output SI.VolumeFlowRate DownstreamKiewa_Inflow_Q;
  output SI.VolumeFlowRate UpstreamKiewa_Inflow_Q_fromReservoir;
  output SI.VolumeFlowRate UpstreamKiewa_Inflow_Q_fromTributary;
equation
  connect(KiewaInflow.QOut, MurrayRiver2.QIn) annotation(
    Line(points = {{36, 22}, {54, 22}}));
  connect(MurrayRiver2.QOut, TerminalDoctorsPoint.QIn) annotation(
    Line(points = {{70, 22}, {80, 22}}));
  connect(InflowHume.QOut, ReservoirHume.QIn) annotation(
    Line(points = {{-72, 22}, {-50, 22}, {-50, 22}, {-50, 22}}));
  connect(ReservoirHume.QOut, MurrayRiver1.QIn) annotation(
    Line(points = {{-34, 22}, {-10, 22}, {-10, 22}, {-10, 22}}));
  connect(ReservoirHume.QOut, MurrayRiver1.QIn) annotation(
    Line(points = {{-34, 22}, {-10, 22}, {-10, 22}, {-10, 22}}));
  connect(Tributary.QOut, KiewaInflow.QIn[2]) annotation(
    Line(points = {{22, 44}, {20, 44}, {20, 22}}));
  connect(InflowTributary.QOut, Tributary.QIn) annotation(
    Line(points = {{20, 74}, {20, 74}, {20, 60}, {20, 60}}));
  connect(MurrayRiver1.QOut, KiewaInflow.QIn[1]) annotation(
    Line(points = {{6, 22}, {20, 22}, {20, 22}, {20, 22}}));
  InflowHume.Q = ReservoirHume_Inflow_Q;
  InflowTributary.Q = Tributary_Inflow_Q;
  ReservoirHume.Q_bottomoutlet = ReservoirHume_Qbottomoutlet;
  ReservoirHume.Q_spill = ReservoirHume_Qspill;
  ReservoirHume.Q_turbine = ReservoirHume_Qturbine;
  ReservoirHume_V = ReservoirHume.V;
  ReservoirHume_Qout = ReservoirHume.QOut.Q;
  DoctorsPoint_Q = TerminalDoctorsPoint.QIn.Q;
  DownstreamKiewa_Inflow_Q = KiewaInflow.QOut[1].Q;
  UpstreamKiewa_Inflow_Q_fromReservoir = KiewaInflow.QIn[1].Q;
  UpstreamKiewa_Inflow_Q_fromTributary = KiewaInflow.QIn[2].Q;
  MurrayRiver1_Q_delayed = MurrayRiver1.Q_delayed;
  MurrayRiver2_Q_delayed = MurrayRiver2.Q_delayed;
  Tributary_Q_delayed = Tributary.Q_delayed;
  annotation(
    Diagram(graphics = {Text(origin = {-75, 5}, extent = {{-23, 11}, {11, -3}}, textString = "Reservoir inflow"), Text(origin = {-23, 15}, extent = {{-33, -13}, {3, 3}}, textString = "Hume Reservoir"), Text(origin = {-3, 11}, extent = {{-11, 3}, {11, -3}}, textString = "MurrayRiver1"), Text(origin = {57, 9}, extent = {{-11, 3}, {11, -3}}, textString = "MurrayRiver2"), Text(origin = {49, 57}, extent = {{-11, 3}, {23, -11}}, textString = "Kiewa"), Text(origin = {89, 9}, extent = {{-19, 5}, {11, -3}}, textString = "Doctor's Point"), Text(origin = {41, 87}, extent = {{-11, 3}, {23, -11}}, textString = "Inflow Kiewa"), Text(origin = {21, 11}, extent = {{-11, 3}, {15, -5}}, textString = "Kiewa inflow")}, coordinateSystem(initialScale = 0.1)));
end ReservoirModel__simulation;
