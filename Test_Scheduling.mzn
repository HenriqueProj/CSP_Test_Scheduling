% Variables from the input file
int: teste_Number = 10;
int: machine_Number;

array[1..10] of int: teste = [2,4,3,4,3,2,1,2,3,5];

% Turn into array of machines 

array[1..machine_Number, 1..teste_Number] of 0..1: m;
array[1..teste_Number] of 0..1: m1 = [1,1,1,1,1,1,1,0,0,1];
array[1..teste_Number] of 0..1: m2 = [1,1,1,1,1,1,0,1,0,0];
array[1..teste_Number] of 0..1: m3 = [1,1,1,1,1,1,0,0,1,1];

% Turn into array of resources
array[1..machine_Number, 1..teste_Number] of 0..1: resources;
array[1..teste_Number] of 0..1: resource_1 = [0,1,1,1,0,0,0,0,0,0];

% Solving starts here
int: Max_span = 100;
array[1..machine_Number, 1..teste_Number] of var tuple (0..Max_span, 0..Max_span): machines;

array[1..teste_Number] of var tuple(0..Max_span,0..Max_span): maquina_1;
array[1..teste_Number] of var tuple(0..Max_span,0..Max_span): maquina_2;
array[1..teste_Number] of var tuple(0..Max_span,0..Max_span): maquina_3;

array[1..machine_Number] of int: machine_times;
var int: time_maq_1;
var int: time_maq_2;
var int: time_maq_3;

% Total time is the maximum of the individual machine times
var int: time = max(time_maq_1, max(time_maq_2, time_maq_3));

% Restriction for machine values: 0 or >= 1

constraint forall(j in 1..machine_Number, i in 1..teste_Number where m[j,i] == 0)(
  machines[j,i].1=0
 );
 
%constraint forall(i in 1..teste_Number where m1[i] == 0) (
%    maquina_1[i].1 = 0
%);
%constraint forall(i in 1..teste_Number where m2[i] == 0) (
%    maquina_2[i].1 = 0
%);
%constraint forall(i in 1..teste_Number where m3[i] == 0) (
%    maquina_3[i].1 = 0
%);

% Ensure that each test is assigned to exactly one machine
constraint forall(i in 1..teste_Number) (
  sum(j in 1..machine_Number) (machines[j,i].1 > 0) == 1
);

%constraint forall(i in 1..teste_Number) (
%  (maquina_1[i].1 > 0) + (maquina_2[i].1 > 0) + (maquina_3[i].1 > 0) == 1
%);

% Ensure that at least one machine is processing each test
constraint forall(i in 1..teste_Number) (
    maquina_1[i].1 != 0 \/ maquina_2[i].1 != 0 \/ maquina_3[i].1 != 0
);

% Ensure that the finish value is the same as the starting value + duration in all machines
constraint forall(i in 1..teste_Number) (
    (maquina_1[i].1 != 0 -> maquina_1[i].2 = maquina_1[i].1 + teste[i]) /\
    (maquina_2[i].1 != 0 -> maquina_2[i].2 = maquina_2[i].1 + teste[i]) /\
    (maquina_3[i].1 != 0 -> maquina_3[i].2 = maquina_3[i].1 + teste[i])
);

% Ensure the finish time is 0 if the machine is not in use
constraint forall(i in 1..teste_Number) (
    (maquina_1[i].1 == 0 -> maquina_1[i].2 = 0) /\
    (maquina_2[i].1 == 0 -> maquina_2[i].2 = 0) /\
    (maquina_3[i].1 == 0 -> maquina_3[i].2 = 0)
);

%Ensure no overlapping within the tests for each machine
constraint forall(i, j in 1..teste_Number where i != j) (
   (maquina_1[i].1 != 0 /\ maquina_1[j].1 != 0) -> (maquina_1[j].1 >= maquina_1[i].2 \/ maquina_1[i].1 >= maquina_1[j].2)
);
constraint forall(i, j in 1..teste_Number where i != j) (
    (maquina_2[i].1 != 0 /\ maquina_2[j].1 != 0) -> (maquina_2[j].1 >= maquina_2[i].2 \/ maquina_2[i].1 >= maquina_2[j].2)
);
constraint forall(i, j in 1..teste_Number where i != j) (
    (maquina_3[i].1 != 0 /\ maquina_3[j].1 != 0) -> (maquina_3[j].1 >= maquina_3[i].2 \/ maquina_3[i].1 >= maquina_3[j].2)
);

constraint forall(i,j in 1..teste_Number where resource_1[i] == 1 /\ resource_1[j] == 1 /\ i != j )(
  (maquina_1[i].1 !=0 /\ maquina_2[j].1 != 0 -> maquina_1[i].1 >= maquina_2[j].2 \/ maquina_2[j].1 >= maquina_1[i].2) 
  /\
  (maquina_3[j].1 !=0 /\ maquina_2[i].1 != 0 -> maquina_2[i].1 >= maquina_3[j].2 \/ maquina_3[j].1 >= maquina_2[i].2) 
  /\
  (maquina_1[j].1 !=0 /\ maquina_3[i].1 != 0 -> maquina_3[i].1 >= maquina_1[j].2 \/ maquina_1[j].1 >= maquina_3[i].2))
;
  
% Calculate the total time for each machine
constraint time_maq_1 = max([maquina_1[i].2 | i in 1..teste_Number]) -1;
constraint time_maq_2 = max([maquina_2[i].2 | i in 1..teste_Number]) -1;
constraint time_maq_3 = max([maquina_3[i].2 | i in 1..teste_Number]) -1;

% Solve by minimizing the total time
solve minimize time;
