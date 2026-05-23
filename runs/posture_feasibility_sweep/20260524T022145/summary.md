# Posture Feasibility Sweep Summary

Run root: `runs/posture_feasibility_sweep/20260524T022145`

## Gates

- `solver_success_fraction_min`: `1.0`
- `contact_present_fraction_min`: `1.0`
- `tail_mean_abs_force_error_N_max`: `0.25`
- `max_tangential_position_error_m_max`: `0.002`
- `max_planar_velocity_slack_m_s_max`: `0.001`
- `max_abs_normal_velocity_slack_m_s_max`: `0.0002`
- `max_qdot_violation_rad_s_max`: `1e-09`
- `max_joint_limit_violation_rad_max`: `1e-09`
- `qdot_saturation_fraction_max`: `0.01`
- `tail_max_qdot_utilization_max`: `0.98`

## Fastest Scale Passing Both E2/E3

- `baseline`: none
- `bend_0p03`: `0.25`
- `bend_0p05`: `0.5`
- `bend_0p075`: `0.75`
- `bend_0p10`: `1.0`

## Cases

| posture | trajectory | scale | pass | failed criteria | base z offset m | force error N | max pos err m | max planar slack m/s | qdot sat frac | tail qdot util |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | e2-figure-eight | `1.0` | `False` | `solver_success_fraction;max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.08097697498404266` | `0.022994130404429502` | `0.014298549809126072` | `0.828` | `0.9999999999999998` |
| baseline | e2-figure-eight | `0.75` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.05043720574356312` | `0.017093692727063747` | `0.011082315402674632` | `0.77` | `0.9999999999999998` |
| baseline | e2-figure-eight | `0.6` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.032725977495626994` | `0.012916929724016035` | `0.008837204805667425` | `0.71225` | `0.9999999999999998` |
| baseline | e2-figure-eight | `0.5` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.020832727965758812` | `0.009886091378418492` | `0.006931203353910178` | `0.65425` | `0.9999999999999998` |
| baseline | e2-figure-eight | `0.35` | `False` | `solver_success_fraction;max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.008575815922278907` | `0.0050362729632133455` | `0.0041272189630289415` | `0.49075` | `0.9999999999999998` |
| baseline | e2-figure-eight | `0.25` | `False` | `solver_success_fraction;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.002573921164182661` | `0.001666702731474482` | `0.0019502636843512571` | `0.3005` | `0.9999999999999998` |
| baseline | e2-figure-eight | `0.2` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.0007787250282253866` | `0.00032479091351769285` | `0.0008416272101666973` | `0.13025` | `0.9999999999999998` |
| baseline | e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.022621162113788083` | `0.017242221453595254` | `0.011087649384373089` | `0.81` | `0.9999999999999998` |
| baseline | e3-circle | `0.75` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.012891020277324527` | `0.011668073043814122` | `0.007739162180545329` | `0.7455` | `0.9999999999999998` |
| baseline | e3-circle | `0.6` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.00644119350334795` | `0.00835595658189906` | `0.005618815383949916` | `0.6815` | `0.9999999999999998` |
| baseline | e3-circle | `0.5` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.004249806777533267` | `0.006200089639492452` | `0.004314517031402206` | `0.6175` | `0.9999999999999998` |
| baseline | e3-circle | `0.35` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.002446035952243627` | `0.00310620858242405` | `0.0024401019469537555` | `0.453` | `0.9999999999999998` |
| baseline | e3-circle | `0.25` | `False` | `max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.0007816570002681134` | `0.0011559659919389111` | `0.0013262589356705513` | `0.23375` | `0.9999999999999998` |
| baseline | e3-circle | `0.2` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `-1.8310546875000003e-05` | `0.0004132670949117756` | `0.00016882932412278057` | `0.0008235304773517502` | `0.04175` | `0.9999999999999998` |
| bend_0p03 | e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.02441103360764771` | `0.017428149717226105` | `0.011458946342148318` | `0.68975` | `0.9999999999999998` |
| bend_0p03 | e2-figure-eight | `0.75` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.012669944033684826` | `0.011480479503407907` | `0.008465693451608228` | `0.5845` | `0.9999999999999998` |
| bend_0p03 | e2-figure-eight | `0.6` | `False` | `solver_success_fraction;max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.007551562585418439` | `0.007263313405027247` | `0.006013856871250193` | `0.47875` | `0.9999999999999998` |
| bend_0p03 | e2-figure-eight | `0.5` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.003657192873556816` | `0.0042296851160473` | `0.004336132609482616` | `0.37425` | `0.9999999999999998` |
| bend_0p03 | e2-figure-eight | `0.35` | `False` | `max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.0007083496782881216` | `0.0003702614442006995` | `0.0010540558992944607` | `0.105` | `0.9999999999999998` |
| bend_0p03 | e2-figure-eight | `0.25` | `True` | `none` | `-8.544921875e-05` | `0.00033819718134071365` | `2.236066698456432e-06` | `9.858570517020254e-08` | `0.0` | `0.06677679449788544` |
| bend_0p03 | e2-figure-eight | `0.2` | `True` | `none` | `-8.544921875e-05` | `0.00033967969628094453` | `1.7888547167202819e-06` | `3.849060024450584e-08` | `0.0` | `0.04036104120069814` |
| bend_0p03 | e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.007263646189180592` | `0.010894565386449092` | `0.007463245098637625` | `0.6855` | `0.9999999999999998` |
| bend_0p03 | e3-circle | `0.75` | `False` | `solver_success_fraction;max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.0025981434194164922` | `0.006677924617720243` | `0.004944322324702247` | `0.57875` | `0.9999999999999998` |
| bend_0p03 | e3-circle | `0.6` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.0018885573703408332` | `0.004511023892149553` | `0.0031029995346862336` | `0.473` | `0.9999999999999998` |
| bend_0p03 | e3-circle | `0.5` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.0015172977600019222` | `0.003101586257473659` | `0.002565996366165191` | `0.36725` | `0.9999999999999998` |
| bend_0p03 | e3-circle | `0.35` | `False` | `max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-8.544921875e-05` | `0.000659759821702256` | `0.0006735864427057224` | `0.0011984341754500704` | `0.095` | `0.9999999999999998` |
| bend_0p03 | e3-circle | `0.25` | `True` | `none` | `-8.544921875e-05` | `0.00033702755471256673` | `1.4999786404264564e-06` | `1.2567374168232972e-07` | `0.0` | `0.06376823246214564` |
| bend_0p03 | e3-circle | `0.2` | `True` | `none` | `-8.544921875e-05` | `0.0003390830321649774` | `1.1999829123519087e-06` | `5.259513866346707e-08` | `0.0` | `0.03862706914110787` |
| bend_0p05 | e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-0.0002545166015625` | `0.0060895962402610125` | `0.010347841434850121` | `0.008085084280504714` | `0.49175` | `0.9999999999999998` |
| bend_0p05 | e2-figure-eight | `0.75` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-0.0002545166015625` | `0.0023578609608497047` | `0.0043994521455123555` | `0.00484047856891499` | `0.32075` | `0.9999999999999998` |
| bend_0p05 | e2-figure-eight | `0.6` | `False` | `solver_success_fraction;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-0.0002545166015625` | `0.001068913994022489` | `0.0008874840707581073` | `0.002506980684978638` | `0.14925` | `0.9999999999999998` |
| bend_0p05 | e2-figure-eight | `0.5` | `True` | `none` | `-0.0002545166015625` | `0.00022861711748045966` | `4.472115995832147e-06` | `2.0938115676595434e-06` | `0.0` | `0.3298684828607961` |
| bend_0p05 | e2-figure-eight | `0.35` | `True` | `none` | `-0.0002545166015625` | `0.0003074629661842254` | `3.1304800530353233e-06` | `6.285538925967551e-08` | `0.0` | `0.05671753230747312` |
| bend_0p05 | e2-figure-eight | `0.25` | `True` | `none` | `-0.0002545166015625` | `0.0003216127649290812` | `2.236056092012599e-06` | `2.2544126621401363e-08` | `0.0` | `0.030203272472060293` |
| bend_0p05 | e2-figure-eight | `0.2` | `True` | `none` | `-0.0002545166015625` | `0.0003240791218575545` | `1.7888441117440193e-06` | `1.3872947371102653e-08` | `0.0` | `0.02192240091528322` |
| bend_0p05 | e3-circle | `1.0` | `False` | `solver_success_fraction;max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-0.0002545166015625` | `0.0019188755759100996` | `0.006080815583843067` | `0.005382609053636665` | `0.4855` | `0.9999999999999998` |
| bend_0p05 | e3-circle | `0.75` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-0.0002545166015625` | `0.0009985102710706006` | `0.0034770807252612764` | `0.002646579333129137` | `0.312` | `0.9999999999999998` |
| bend_0p05 | e3-circle | `0.6` | `False` | `max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-0.0002545166015625` | `0.0007594207795827934` | `0.0014629386868748443` | `0.002019406894682985` | `0.1385` | `0.9999999999999998` |
| bend_0p05 | e3-circle | `0.5` | `True` | `none` | `-0.0002545166015625` | `0.00015262486160567913` | `2.9999572818635683e-06` | `1.2536737267443166e-06` | `0.0` | `0.23215795053054597` |
| bend_0p05 | e3-circle | `0.35` | `True` | `none` | `-0.0002545166015625` | `0.00030837665682645235` | `2.0999700973295497e-06` | `8.312213829108873e-08` | `0.0` | `0.05206517218087878` |
| bend_0p05 | e3-circle | `0.25` | `True` | `none` | `-0.0002545166015625` | `0.00032238335323937827` | `1.499978640960306e-06` | `3.206014457355962e-08` | `0.0` | `0.027197697055544562` |
| bend_0p05 | e3-circle | `0.2` | `True` | `none` | `-0.0002545166015625` | `0.00032452014879567057` | `1.1999829127732454e-06` | `2.0312785364937355e-08` | `0.0` | `0.019713748645479885` |
| bend_0p075 | e2-figure-eight | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-0.0005566406250000001` | `0.002108501096022637` | `0.002538656201726373` | `0.004109752962304516` | `0.22225` | `0.9999999999999998` |
| bend_0p075 | e2-figure-eight | `0.75` | `True` | `none` | `-0.0005566406250000001` | `0.0002418895519935116` | `6.708177242633557e-06` | `1.4833926954542584e-06` | `0.0` | `0.29367168645797354` |
| bend_0p075 | e2-figure-eight | `0.6` | `True` | `none` | `-0.0005566406250000001` | `0.00015222225653850895` | `5.366541226645658e-06` | `1.4049385332534674e-07` | `0.0` | `0.09482587346253052` |
| bend_0p075 | e2-figure-eight | `0.5` | `True` | `none` | `-0.0005566406250000001` | `9.16517127855343e-05` | `4.47211721782408e-06` | `6.344637515032022e-08` | `0.0` | `0.0598383803673632` |
| bend_0p075 | e2-figure-eight | `0.35` | `True` | `none` | `-0.0005566406250000001` | `0.0002786374465354646` | `3.1304812072971583e-06` | `2.518733897208631e-08` | `0.0` | `0.033805527388188567` |
| bend_0p075 | e2-figure-eight | `0.25` | `True` | `none` | `-0.0005566406250000001` | `0.0002975224089730477` | `2.2360572021348384e-06` | `1.2835626195547886e-08` | `0.0` | `0.020172015884786225` |
| bend_0p075 | e2-figure-eight | `0.2` | `True` | `none` | `-0.0005566406250000001` | `0.00030102973878535556` | `1.7888452000704736e-06` | `8.96120876469911e-09` | `0.0` | `0.015064473813590459` |
| bend_0p075 | e3-circle | `1.0` | `False` | `max_tangential_position_error_m;max_planar_velocity_slack_m_s;qdot_saturation_fraction;tail_max_qdot_utilization` | `-0.0005566406250000001` | `0.0008917036172458414` | `0.0028046925749286578` | `0.002652310734312028` | `0.22875` | `0.9999999999999998` |
| bend_0p075 | e3-circle | `0.75` | `True` | `none` | `-0.0005566406250000001` | `0.0003530988511318245` | `4.499935930180842e-06` | `1.9027251309992462e-06` | `0.0` | `0.33380189269426025` |
| bend_0p075 | e3-circle | `0.6` | `True` | `none` | `-0.0005566406250000001` | `0.00016165344784858427` | `3.5999487442075597e-06` | `1.9101233852717096e-07` | `0.0` | `0.09151266051320119` |
| bend_0p075 | e3-circle | `0.5` | `True` | `none` | `-0.0005566406250000001` | `0.00013224077831098358` | `2.999957286868429e-06` | `8.843769136154e-08` | `0.0` | `0.053824734884332225` |
| bend_0p075 | e3-circle | `0.35` | `True` | `none` | `-0.0005566406250000001` | `0.00028585324365880014` | `2.0999701008321694e-06` | `3.627696754310672e-08` | `0.0` | `0.02861822736654121` |
| bend_0p075 | e3-circle | `0.25` | `True` | `none` | `-0.0005566406250000001` | `0.0002997197427428855` | `1.4999786434610453e-06` | `1.906012308389773e-08` | `0.0` | `0.01862812916038475` |
| bend_0p075 | e3-circle | `0.2` | `True` | `none` | `-0.0005566406250000001` | `0.00030193382923368925` | `1.1999829147727592e-06` | `1.3448874798111861e-08` | `0.0` | `0.014970851348463913` |
| bend_0p10 | e2-figure-eight | `1.0` | `True` | `none` | `-0.0009710693359375` | `0.0004002236522971103` | `8.944242301072789e-06` | `3.4331973232314785e-07` | `0.0` | `0.15222223080960362` |
| bend_0p10 | e2-figure-eight | `0.75` | `True` | `none` | `-0.0009710693359375` | `0.0002867238516034654` | `6.708181951861575e-06` | `9.75023279306383e-08` | `0.0` | `0.08467945238003273` |
| bend_0p10 | e2-figure-eight | `0.6` | `True` | `none` | `-0.0009710693359375` | `0.00017049709897981602` | `5.366545749020208e-06` | `5.0233909170271204e-08` | `0.0` | `0.05680241391370145` |
| bend_0p10 | e2-figure-eight | `0.5` | `True` | `none` | `-0.0009710693359375` | `0.00010125056974845448` | `4.472121616546188e-06` | `3.168111111568034e-08` | `0.0` | `0.04081884018150708` |
| bend_0p10 | e2-figure-eight | `0.35` | `True` | `none` | `-0.0009710693359375` | `0.0002474744028154419` | `3.130485421996875e-06` | `1.6641491347998468e-08` | `0.0` | `0.02495742583727578` |
| bend_0p10 | e2-figure-eight | `0.25` | `True` | `none` | `-0.0009710693359375` | `0.00027029215479819845` | `2.2360612951310893e-06` | `9.870347713009761e-09` | `0.0` | `0.015446939346832467` |
| bend_0p10 | e2-figure-eight | `0.2` | `True` | `none` | `-0.0009710693359375` | `0.0002746695347656947` | `1.7888492325043605e-06` | `7.331591747457556e-09` | `0.0` | `0.011664441680852096` |
| bend_0p10 | e3-circle | `1.0` | `True` | `none` | `-0.0009710693359375` | `0.000821132687569398` | `5.999914591097446e-06` | `1.1696023075496035e-06` | `0.0` | `0.27981610187783346` |
| bend_0p10 | e3-circle | `0.75` | `True` | `none` | `-0.0009710693359375` | `0.00033458085355989487` | `4.499935943491119e-06` | `1.6837893294863446e-07` | `0.0` | `0.08969352059852591` |
| bend_0p10 | e3-circle | `0.6` | `True` | `none` | `-0.0009710693359375` | `0.000152889721569891` | `3.59994875485513e-06` | `7.961074434499636e-08` | `0.0` | `0.05169938995405445` |
| bend_0p10 | e3-circle | `0.5` | `True` | `none` | `-0.0009710693359375` | `0.0001109366409070156` | `2.9999572957408043e-06` | `4.9329469504360294e-08` | `0.0` | `0.035838083422613166` |
| bend_0p10 | e3-circle | `0.35` | `True` | `none` | `-0.0009710693359375` | `0.0002600237904927083` | `2.099970107041499e-06` | `2.553234089131805e-08` | `0.0` | `0.025756861113634587` |
| bend_0p10 | e3-circle | `0.25` | `True` | `none` | `-0.0009710693359375` | `0.000273707070894369` | `1.4999786478946057e-06` | `1.5096997025151107e-08` | `0.0` | `0.01862462234126951` |
| bend_0p10 | e3-circle | `0.2` | `True` | `none` | `-0.0009710693359375` | `0.000275993529207188` | `1.1999829183181331e-06` | `1.1179352075812174e-08` | `0.0` | `0.014967972418866146` |
