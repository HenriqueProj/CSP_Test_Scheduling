int: Max_span = 100;
int: teste_Number = 10;

array[1..teste_Number] of var 0..Max_span: maquina_1;
array[1..teste_Number] of var 0..Max_span: maquina_2;
array[1..teste_Number] of var 0..Max_span: maquina_3;

var int: time_maq_1;
var int: time_maq_2;
var int: time_maq_3;

array[1..10] of int: teste = [2,4,3,4,3,2,1,2,3,5];
array[1..teste_Number] of 0..1: resource_1 = [0,1,1,1,0,0,0,0,0,0];

var int: time = max(time_maq_1, max(time_maq_2, time_maq_3));

% Restriction for machine values: -1, 0 or >= 1
constraint forall(i in 1..teste_Number)(maquina_1[i] = -1 \/ maquina_1[i] = 0 \/ maquina_1[i] >= 1);
constraint forall(i in 1..teste_Number)(maquina_2[i] = -1 \/ maquina_2[i] = 0 \/ maquina_2[i] >= 1);
constraint forall(i in 1..teste_Number)(maquina_3[i] = -1 \/ maquina_3[i] = 0 \/ maquina_3[i] >= 1);

% Ensure that each test is assigned to exactly one machine
constraint forall(i in 1..teste_Number) (maquina_1[i] = 0 \/ (maquina_1[i] > 0 /\ maquina_2[i] = 0 /\ maquina_3[i] = 0));
constraint forall(i in 1..teste_Number) (maquina_2[i] = 0 \/ (maquina_2[i] > 0 /\ maquina_1[i] = 0 /\ maquina_3[i] = 0));
constraint forall(i in 1..teste_Number) (maquina_3[i] = 0 \/ (maquina_3[i] > 0 /\ maquina_2[i] = 0 /\ maquina_1[i] = 0));

% Ensure that at least one machine is processing each test
constraint forall(i in 1..teste_Number) (maquina_1[i] != 0 \/ maquina_2[i] != 0 \/ maquina_3[i] != 0);
constraint forall(i in 1..teste_Number)(maquina_1[i] = teste[i] \/ maquina_2[i] = teste[i] \/ maquina_3[i] = teste[i]);


array[1..teste_Number] of 0..1: m1;
m1 = [1,1,1,1,1,0,0,0,0,0];
array[1..teste_Number] of 0..1: m2;
m2 = [0,0,0,0,0,1,1,0,1,1];
array[1..teste_Number] of 0..1: m3;
m3 = [0,1,1,1,1,1,1,1,1,1];

constraint forall(i in 1..10)( (maquina_1[i] = 0 /\ m1[i] = 0) \/ m1[i] != 0 );
constraint forall(i in 1..10)( (maquina_2[i] = 0 /\ m2[i] = 0) \/ m2[i] != 0 );
constraint forall(i in 1..10)( (maquina_3[i] = 0 /\ m3[i] = 0) \/ m3[i] != 0 );

% Time calculation for each machine to accumulate previous test times
% We create a cumulative variable to accumulate the test durations for each machine
array[1..teste_Number] of var 0..Max_span: acumulado_maq_1;
array[1..teste_Number] of var 0..Max_span: acumulado_maq_2;
array[1..teste_Number] of var 0..Max_span: acumulado_maq_3;

% The first element of acumulado is just the time of the first test
constraint acumulado_maq_1[1] = maquina_1[1];
constraint acumulado_maq_2[1] = maquina_2[1];
constraint acumulado_maq_3[1] = maquina_3[1];

% For each subsequent test, the accumulated time is the previous accumulated time + current test
constraint forall(i in 2..teste_Number) (
    acumulado_maq_1[i] = acumulado_maq_1[i-1] + maquina_1[i]
);
constraint forall(i in 2..teste_Number) (
    acumulado_maq_2[i] = acumulado_maq_2[i-1] + maquina_2[i]
);
constraint forall(i in 2..teste_Number) (
    acumulado_maq_3[i] = acumulado_maq_3[i-1] + maquina_3[i]
);

% Calculate the total time for each machine
constraint time_maq_1 = acumulado_maq_1[teste_Number];
constraint time_maq_2 = acumulado_maq_2[teste_Number];
constraint time_maq_3 = acumulado_maq_3[teste_Number];

% Make sure that the intervals between starting time and finishing time of tests using same resources are not overlapping
constraint forall(i in 1..teste_Number where  resource_1[i] = 1 )(
    (acumulado_maq_1[i] - teste[i] <= acumulado_maq_2[i] \/ acumulado_maq_2[i] - teste[i] <= acumulado_maq_1[i]) /\
    (acumulado_maq_2[i] - teste[i] <= acumulado_maq_3[i] \/ acumulado_maq_3[i] - teste[i] <= acumulado_maq_2[i]) /\
    (acumulado_maq_3[i] - teste[i] <= acumulado_maq_1[i] \/ acumulado_maq_1[i] - teste[i] <= acumulado_maq_3[i])
);


% Solve by minimizing the total time
solve minimize time;


