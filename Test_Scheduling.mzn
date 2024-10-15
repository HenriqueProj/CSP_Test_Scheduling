include "diffn.mzn";
include "cumulative.mzn";

% Variables from the input file
int: teste_Number;
int: machine_Number;
int: resource_Number;

% Test durations
array[1..teste_Number] of int: teste;
% Start and end times for each test
array[1..teste_Number] of var 1..sum(teste)+1 - min(teste): test_start;

% Machines that can run each test
array[1..teste_Number] of var 1..machine_Number: test_machine;

% Machines and resources
array[1..machine_Number, 1..teste_Number] of 0..1: m;
array[1..resource_Number, 1..teste_Number] of 0..1: resources;

% Make sure test is assigned to a machine that can run it
constraint forall(i in 1..teste_Number)(
    m[test_machine[i], i] == 1
);

% Make sure every machine has at least one test
constraint forall(v in 1..machine_Number) (
    exists(i in 1..teste_Number)(test_machine[i] == v)
);

% Check if resources are right
constraint forall(r in 1..resource_Number)( 
    forall(i, j in 1..teste_Number where resources[r,i] == 1 /\ resources[r,j] == 1 /\ i != j)(
        test_start[i] + teste[i] <= test_start[j] \/ test_start[j] + teste[j] <= test_start[i]
    )
);

% Arrange the tests
%constraint forall(m1 in 1..machine_Number) (
%  cumulative(
%  test_start,
%  teste,
%  [m[m1,t] | t in 1..teste_Number],
%  1)
%);
constraint diffn(test_start, test_machine, teste, [1 | i in 1..teste_Number]);


% Total time is the maximum of the individual machine times
var int: time = max([test_start[i] + teste[i] | i in 1..teste_Number]) - 1;

% Lowest possible time -> max between the biggest test and the time required for the largest resource
var int: best_time = max(max(teste), max(r in 1..resource_Number) (sum(i in 1..teste_Number where resources[r, i] == 1) (teste[i])));

constraint time >= best_time;

% Solve by minimizing the total time
solve :: int_search(
    test_start,
    smallest, indomain_min,
    complete
) minimize time;
