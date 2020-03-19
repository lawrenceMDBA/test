model ReservoirModel
  import SI = Modelica.SIunits;
  // Schematization elements
  Deltares.ChannelFlow.SimpleRouting.Reservoir.Reservoir ReservoirHume annotation(
    Placement(visible = true, transformation(origin = {-42, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.SimpleRouting.BoundaryConditions.Inflow InflowHume annotation(
    Placement(visible = true, transformation(origin = {-80, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  //Deltares.ChannelFlow.SimpleRouting.Branches.Steady MurrayRiver1 annotation(
  Deltares.ChannelFlow.SimpleRouting.Branches.Delay MurrayRiver1(duration = 1.08*10^4)  annotation(
    Placement(visible = true, transformation(origin = {-2, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.SimpleRouting.Nodes.Node KiewaInflow (nin = 2, nout = 1) annotation(Placement(visible = true, transformation(origin = {28, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.SimpleRouting.Branches.Delay MurrayRiver2(duration = 1.8*10^4) annotation(
    Placement(visible = true, transformation(origin = {62, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.SimpleRouting.BoundaryConditions.Terminal TerminalDoctorsPoint annotation(
    Placement(visible = true, transformation(origin = {88, 22}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Deltares.ChannelFlow.SimpleRouting.Branches.Delay Tributary(duration = 2.16*10^4) annotation(
    Placement(visible = true, transformation(origin = {20, 52}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Deltares.ChannelFlow.SimpleRouting.BoundaryConditions.Inflow InflowTributary annotation(
    Placement(visible = true, transformation(origin = {20, 82}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  // variable used to represent the absolute value of the derivative of Qturbine, used to smoothen
  //    operation of the turbine.
  Real ReservoirHume_absQturbder(min = 0);
  // Time series
  input SI.VolumeFlowRate ReservoirHume_Inflow_Q(fixed = true);
  input SI.VolumeFlowRate Tributary_Inflow_Q(fixed = true);
  input SI.VolumeFlowRate ReservoirHume_Qturbine(fixed = false);
  input SI.VolumeFlowRate ReservoirHume_Qspill(fixed = false);  
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
  ReservoirHume.Q_spill = ReservoirHume_Qspill;
  ReservoirHume.Q_turbine = ReservoirHume_Qturbine;
  ReservoirHume_V = ReservoirHume.V;
  ReservoirHume_Qout = ReservoirHume.QOut.Q;
  DoctorsPoint_Q = TerminalDoctorsPoint.QIn.Q;
  DownstreamKiewa_Inflow_Q = KiewaInflow.QOut[1].Q;
  UpstreamKiewa_Inflow_Q_fromReservoir = KiewaInflow.QIn[1].Q;
  UpstreamKiewa_Inflow_Q_fromTributary = KiewaInflow.QIn[2].Q;
    end ReservoirModel;
