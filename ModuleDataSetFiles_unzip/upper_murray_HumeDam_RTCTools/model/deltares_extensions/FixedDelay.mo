// Only works if no interpolation is needed, so the delay should be divisable by the timestep
// in the problem.
block FixedDelay
  extends Deltares.ChannelFlow.Internal.QSISO;
  input Real Q_delayed;
equation
	QOut.Q = Q_delayed;
  annotation(Icon(graphics = {Text(extent = {{-25, 25}, {25, -25}}, textString = "τ")}, coordinateSystem(initialScale = 0.1)));
end FixedDelay;