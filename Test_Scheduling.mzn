include "diffn.mzn";
include "cumulative.mzn";

% Variables from the input file
int: teste_Number;
int: machine_Number;
int: resource_Number;
int: pointer;

% Test durations
array[1..teste_Number] of int: teste;

% Start and end times for each test
array[1..teste_Number] of var 1..pointer + 1 - min(teste): test_start;

% Machines that can run each test
array[1..teste_Number] of var 1..machine_Number: test_machine;

% Machines and resources
array[1..machine_Number, 1..teste_Number] of 0..2: m;
array[1..resource_Number, 1..teste_Number] of 0..1: resources;

% Groups of machines to help break simetry
array[1..machine_Number] of int: color_of_machines;

array[1..teste_Number] of int: test_no_resources;



% Garantir que o tempo de execução siga a ordem dentro dos grupos de máquinas
%constraint forall(i in 1..machine_Number-1, j in i+1..machine_Number where color_of_machines[i] == color_of_machines[j]) (
%    let {
%        var int: t_i = max([test_start[t] + teste[t] | t in 1..teste_Number where test_machine[t] == i]),
%        var int: t_j = max([test_start[t] + teste[t] | t in 1..teste_Number where test_machine[t] == j])
%    } in
%        t_i > t_j
%);

var int: time;
constraint time = max([test_start[i] + teste[i] | i in 1..teste_Number]) - 1;

constraint time <= pointer;

% Make sure test is assigned to a machine that can run it
constraint forall(i in 1..teste_Number)(
    m[test_machine[i], i] >= 1
);

% Make sure that if they are any tests that can only be executed in a specific machine, make sure to only explore those scenarios
constraint forall(j in 1..machine_Number, i in 1..teste_Number where m[j,i]==2) (
    test_machine[i] = j
);

% Check if resources are right
constraint forall(r in 1..resource_Number)(
    cumulative([test_start[i] | i in 1..teste_Number where resources[r, i] == 1],
               [teste[i] | i in 1..teste_Number where resources[r, i] == 1],
               [1 | i in 1..teste_Number where resources[r, i] == 1],
               1)
);

constraint diffn(test_start, test_machine, teste, [1 | i in 1..teste_Number]);

constraint forall(i in 1..machine_Number)(
    forall(t in 1..teste_Number-1 where test_machine[t] == i /\ test_no_resources[t] == 1 /\ test_machine[t+1] == i /\ test_no_resources[t+1] == 1) (
        abs(test_start[t+1] - (test_start[t] + teste[t])) > 0 -> test_start[t] + teste[t] == test_start[t+1]
    )
);

% Arrange the m
%constraint forall(m1 in 1..machine_Number) (
%  cumulative(
%  test_start,
%  teste,
%  [m[m1,t] | t in 1..teste_Number],
%  1)
%);

% Total time is the maximum of the individual machine times
% Lowest possible time -> max between the biggest test and the time required for the largest resource
%var int: best_time = max(max(teste), max(r in 1..resource_Number) (sum(i in 1..teste_Number where resources[r, i] == 1) (teste[i])));


% Now sort the tests by combined_priority
solve :: int_search(
    [test_start[i] | i in 1..teste_Number],
    input_order,
    indomain_split,
    complete
) satisfy;
%[test_start[i] | i in 1..teste_Number where sum(r in 1..resource_Number)(resources[r, i] == 1) > 0] ++
