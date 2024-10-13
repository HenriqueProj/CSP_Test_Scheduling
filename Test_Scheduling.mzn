
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
int: Max_span =  sum(teste) - min(teste) + 1;
int: Machines_per_Combination;
int: Number_of_Combinations;
array[1..Number_of_Combinations, 1..Machines_per_Combination] of -1..machine_Number :color_of_machines ;

array[1..machine_Number, 1..teste_Number] of var tuple (0..Max_span, 0..Max_span): machines;

array[1..machine_Number] of var int: time_per_machine;

constraint forall(i in 1..Number_of_Combinations) (
    forall(j in 1..Machines_per_Combination - 1 where color_of_machines[i, j+1] != -1) (
        let {
            var int: machine1 = color_of_machines[i,j];
            var int: machine2 = color_of_machines[i,j+1];
            var int: max_finish_time_1 = max([machines[machine1 + 1,k1].2 | k1 in 1..teste_Number]);
            var int: max_finish_time_2 = max([machines[machine2 + 1,k2].2 | k2 in 1..teste_Number])
        } in
        max_finish_time_1 >= max_finish_time_2
    )
);


% Restriction for machine values: 0 or >= 1
constraint forall(j in 1..machine_Number, i in 1..teste_Number where m[j,i] == 0)(
  machines[j,i].1=0 /\ machines[j,i].2=0
);


% Ensure each test is assigned to exactly one machine
constraint forall(i in 1..teste_Number) (
    sum(j in 1..machine_Number) (machines[j,i].1 > 0) == 1
);


% Ensure that the finish value is the same as the starting value + duration in all machines
constraint forall(i in 1..teste_Number) (
    forall(j in 1..machine_Number where machines[j,i].1 == 0) (
        machines[j,i].2 = 0
    )
);

% Ensure that the finish value is the same as the start value + duration in all machines
constraint forall(i in 1..teste_Number) (
    forall(j in 1..machine_Number where  (machines[j,i].1 != 0)) (
        machines[j,i].2 = machines[j,i].1 + teste[i]
    )
);


% Ensure no overlapping for tests in the same machine
constraint forall(k in 1..machine_Number) (
    forall(i, j in 1..teste_Number where (i != j /\ machines[k,i].1 != 0 /\ machines[k,j].1 != 0)) ( 
        (machines[k,j].1 == machines[k,i].2 \/ machines[k,i].1 == machines[k,j].2)
    )
);


constraint forall(r in 1..resource_Number)( 
    forall(i, j in 1..teste_Number where resources[r,i] == 1 /\ resources[r,j] == 1 /\ i != j)(
        forall(m1, m2 in 1..machine_Number where (m1 != m2 /\ machines[m1,i].1 != 0 /\ machines[m2,j].1 != 0))(
            (machines[m1,i].1 >= machines[m2,j].2 \/ machines[m2,j].1 >= machines[m1,i].2)
        )
    )
);

constraint forall(j in 1..machine_Number) (
  sum(i in 1..teste_Number) (machines[j,i].1 ==1 ) == 1
);
  
constraint forall(m1 in 1..machine_Number)(
    time_per_machine[m1] = max([machines[m1,i].2 | i in 1..teste_Number]) -1
);


% Total time is the maximum of the individual machine times
var int: time = max(time_per_machine);

% Calcular o tempo ótimo com base nos testes que requerem recursos globais
var int: best_time = max(max(teste), max(r in 1..resource_Number) (sum(i in 1..teste_Number where resources[r, i] == 1) (teste[i])));

constraint time >= best_time /\ time <= sum(teste);
% Solve by minimizing the total time
solve:: int_search([machines[j,i].2 | j in 1..machine_Number, i in 1..teste_Number], input_order, indomain_split) minimize time;
