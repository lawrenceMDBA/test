| How to | U ![](RackMultipart20200526-4-13kuing_html_736a5355b0591997.png) RBS - Set Hume Release Forecast |
| --- | --- |
| Description | Create modifier to set Hume Release Forecast in URBS model |
| Comments | _i ![](RackMultipart20200526-4-13kuing_html_60f481272685988a.png) talic_ phrases taken from the book &quot;Flood Forecasting: a Global Perspective&quot;.Please be aware that the screenshots may deviate slightly from the application |
| version | 2016-01 |

Define multiple release patterns (Forecast and What-If scenario) on an hourly timestep.

Note: In the ensemble run only the Hume Release Forecast is considered, the What-If Hume Release Scenario is not.

Q\_Release is by default empty (left column). The user can define a release pattern via the modifiers (right column). The set release pattern is used in the URBS run (see second figure of model output).

**Note: it is necessary to start the release pattern at T0, so either enter leading zeros if you want to start to release later, or start with the current release value if this applicable****.**

![](RackMultipart20200526-4-13kuing_html_1b8602135522ec93.png)

The defined release pattern can be visually checked against the total maximum, which is the sum of the maximum release via valves, hydro and spillway gates based on the level in the dam.
 Note 1: Discharge is calculated via a conversion based on ReservoirOutletRatingTables, for which extrapolation is not allowed. This means that when the level in the dam is outside this range, no outflow discharge can be calculated or displayed.

Note 2: The outflow through hydro can only be calculated after the below model has been run as well (Heywoods level is required). If a previous run (even with an older T0) is available, this will be used. With this hydro outflow, the Q\_out\_fcst total max cannot be computed and will not be shown.

![](RackMultipart20200526-4-13kuing_html_f34a2d9442c1889.png)