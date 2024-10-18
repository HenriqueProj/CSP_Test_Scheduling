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

% Make sure there is no overlapp between tests in the same machine
constraint diffn(test_start, test_machine, teste, [1 | i in 1..teste_Number]);

% Make sure every machine has at least one test
constraint forall(v in 1..machine_Number) (
    exists(i in 1..teste_Number)(test_machine[i] == v)
);

% Now sort the tests by combined_priority
solve :: int_search(
    [test_start[i] | i in 1..teste_Number],
    input_order,
    indomain_split,
) satisfy;