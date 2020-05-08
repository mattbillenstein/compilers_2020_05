/*
Statements([27] VarDef([2] x, int, Integer([1] 1)),VarDef([4] y, int, Integer([3] 0)),PrintStatement(BinOp([14] ||, Bool([5] True), Grouping([13] BinOp([12] ==, BinOp([10] /, LocationLookup([7] Var([6] x)), LocationLookup([9] Var([8] y))), Integer([11] 0))))),PrintStatement(BinOp([25] &&, Bool([16] False), Grouping([24] BinOp([23] ==, BinOp([21] /, LocationLookup([18] Var([17] x)), LocationLookup([20] Var([19] y))), Integer([22] 0))))))
*/
#include <stdio.h>
int main(){
int x;  
int y;  
int _t10;
int _t12;
int _t14;
int _t21;
int _t23;
int _t25;

x = 1;
y = 0;
_t10 = x / y;  
_t12 = _t10 == 0;  
_t14 = 1 || _t12;  
printf("%i\n", _t14);  
_t21 = x / y;  
_t23 = _t21 == 0;  
_t25 = 0 && _t23;  
printf("%i\n", _t25);  
}
