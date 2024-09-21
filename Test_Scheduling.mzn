
% Use this editor as a MiniZinc scratch book
int: Max_span = 100;
array[1..teste_Number] of var 0..Max_span: maquina_1;
array [1..teste_Number] of var 0..Max_span: maquina_2;
array [1..teste_Number] of var 0..Max_span: maquina_3;

var int: time_maq_1 ;
var int: time_maq_2 ;
var int: time_maq_3 ;

int: teste_Number = 10;
array [1..teste_Number] of 0..1: resource_1;

array [1..10] of int: teste;

predicate alldifferent(array[int] of var int: x) =
    forall(i, j in index_set(x) where i < j) (x[i] != x[j]);



teste = [2,4,3,4,3,2,1,2,3,5];
resource_1 = [0,1,1,1,0,0,0,0,0,0];
%maquina_1 = [-1,-1,-1,-1,-1,-1,-1,0,0,-1];
%maquina_2= [-1,-1,-1,-1,-1,-1,0,-1,0,-1];
%maquina_3= [-1,-1,-1,-1,-1,-1,0,0,-1,-1];

var int: time = max(time_maq_1, max(time_maq_2,time_maq_3));

%array[int] of var int: valid_values_1 = [maquina_1[i] | i in 1..10 where maquina_1[i] != 0 /\ maquina_1[i] != -1];
%constraint alldifferent(valid_values_1);
constraint forall(i in 1..10)(maquina_1[i] = -1 \/ maquina_1[i] = 0 \/ maquina_1[i] >= 1);

%array[int] of var int: valid_values_2 = [maquina_2[i] | i in 1..10 where maquina_2[i] != 0 /\ maquina_2[i] != -1];
%constraint alldifferent(valid_values_2);
constraint forall(i in 1..10)(maquina_2[i] = -1 \/ maquina_2[i] = 0 \/ maquina_2[i] >= 1);

%array[int] of var int: valid_values_3 = [maquina_3[i] | i in 1..10 where maquina_3[i] != 0 /\ maquina_3[i] != -1];
%constraint alldifferent(valid_values_3);
constraint forall(i in 1..10)(maquina_3[i] = -1 \/ maquina_3[i] = 0 \/ maquina_3[i] >= 1);

%constraint forall(i in 1..10)((maquina_1[i]-maquina_2[i] > teste[i] \/maquina_2[i]-maquina_1[i] > teste[i]) /\(maquina_3[i]-maquina_2[i] > teste[i] \/maquina_2[i]-maquina_3[i] > teste[i])/\ (maquina_1[i]-maquina_3[i] > teste[i] \/ maquina_3[i]-maquina_1[i] > teste[i]));


constraint forall(i in 1..10) (maquina_1[i]= 0  \/ (maquina_1[i] > 0 /\ maquina_2[i] = 0 /\ maquina_3[i] = 0));
constraint forall(i in 1..10) (maquina_2[i]= 0  \/ (maquina_2[i] > 0 /\ maquina_1[i] = 0 /\ maquina_3[i] = 0));
constraint forall(i in 1..10) (maquina_3[i]= 0  \/ (maquina_3[i] > 0 /\ maquina_2[i] = 0 /\ maquina_1[i] = 0));

constraint forall(i in 1..10) (maquina_1[i]!= 0 \/ maquina_2[i] != 0 \/ maquina_3[i]!=0);
constraint forall(i in 1..10)(maquina_1[i]= teste[i] \/ maquina_2[i] = teste[i] \/ maquina_3[i] =teste[i]);

constraint time_maq_1 = sum(maquina_1);
constraint time_maq_2 = sum(maquina_2);
constraint time_maq_3 = sum(maquina_3);



solve minimize time;
