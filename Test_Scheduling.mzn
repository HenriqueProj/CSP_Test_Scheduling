% Variables from the input file
int: teste_Number;
int: machine_Number;
int: resource_Number;

array[1..teste_Number] of int: teste;

% Initial array of machines
array[1..machine_Number, 1..teste_Number] of 0..1: m;

array[1..resource_Number, 1..teste_Number] of 0..1: resources;

% Solving starts here
% OPTIMIZING MAX_SPAN
int: Max_span = sum(teste) + 1;

array[1..machine_Number, 1..teste_Number] of var tuple (0..Max_span, 0..Max_span): machines;



% Restriction for machine values: 0 or >= 1
constraint forall(j in 1..machine_Number, i in 1..teste_Number where m[j,i] == 0)(
  machines[j,i].1=0 /\ machines[j,i].2=0
 );


% Ensure that each test is assigned to exactly one machine
constraint forall(i in 1..teste_Number) (
  sum(j in 1..machine_Number) (machines[j,i].1 > 0) == 1
);


% Ensure that the finish value is the same as the starting value + duration in all machines
constraint forall(i in 1..teste_Number) (
    forall(j in 1..machine_Number) (
        machines[j,i].1 == 0 -> machines[j,i].2 = 0
    )
);

constraint forall(i in 1..teste_Number) (
    forall(j in 1..machine_Number) (
        machines[j,i].1 != 0 -> machines[j,i].2 = machines[j,i].1 + teste[i]
    )
);


%Ensure no overlapping within the tests for each machine
constraint forall(i, j in 1..teste_Number where i != j) (
   forall(k in 1..machine_Number) (
       (machines[k,i].1 != 0 /\ machines[k,j].1 != 0) -> 
       (machines[k,j].1 >= machines[k,i].2 \/ machines[k,i].1 >= machines[k,j].2)
   )
);


constraint forall(r in 1..resource_Number)( 
    forall(i, j in 1..teste_Number where resources[r,i] == 1 /\ resources[r,j] == 1 /\ i != j)(
        forall(m1, m2 in 1..machine_Number where m1 != m2)(
            (machines[m1,i].1 != 0 /\ machines[m2,j].1 != 0) -> 
            (machines[m1,i].1 >= machines[m2,j].2 \/ machines[m2,j].1 >= machines[m1,i].2)
        )
    )
);


array[1..machine_Number] of var int: time_per_machine;
  
constraint forall(m1 in 1..machine_Number)(
    time_per_machine[m1] = max([machines[m1,i].2 | i in 1..teste_Number]) - 1
);


% OPTIMIZATIONS

constraint forall(j in 1..machine_Number) (
  sum(i in 1..teste_Number) (machines[j,i].1 == 1) == 1
);


% Total time is the maximum of the individual machine times
var int: time = max(time_per_machine);


% Solve by minimizing the total time
solve minimize time;