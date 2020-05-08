#include <stdio.h>
int main(){
int _t2;  // VarDef([2] n, int, Integer([1] 0))
int _t8;
int _t13;
int _t23;
int _t30;

_t2 = 0;
LL1:  // While([28] Bool([3] True), Statements([27] Assign([9] Var([4] n), BinOp([8] +, LocationLookup([6] Var([5] n)), Integer([7] 1))),IfConditional([16] BinOp([13] ==, LocationLookup([11] Var([10] n)), Integer([12] 5)), Statements([15] ContinueStatement([14]))),PrintStatement(LocationLookup([18] Var([17] n))),IfConditional([26] BinOp([23] >, LocationLookup([21] Var([20] n)), Integer([22] 10)), Statements([25] Break([24])))))
if (_t3) goto LL2;
goto LL3;
LL2: //Statements([27] Assign([9] Var([4] n), BinOp([8] +, LocationLookup([6] Var([5] n)), Integer([7] 1))),IfConditional([16] BinOp([13] ==, LocationLookup([11] Var([10] n)), Integer([12] 5)), Statements([15] ContinueStatement([14]))),PrintStatement(LocationLookup([18] Var([17] n))),IfConditional([26] BinOp([23] >, LocationLookup([21] Var([20] n)), Integer([22] 10)), Statements([25] Break([24]))))
{
_t8 = _t5 + 1;  // BinOp([8] +, LocationLookup([6] Var([5] n)), Integer([7] 1))
_t4 = _t8;  // Assign([9] Var([4] n), BinOp([8] +, LocationLookup([6] Var([5] n)), Integer([7] 1)))
_t13 = _t10 == 5;  // BinOp([13] ==, LocationLookup([11] Var([10] n)), Integer([12] 5))
if (_t13) goto LL4; // IfConditional([16] BinOp([13] ==, LocationLookup([11] Var([10] n)), Integer([12] 5)), Statements([15] ContinueStatement([14])))
goto LL5;
LL4: //Statements([15] ContinueStatement([14]))
{
goto LL1;  // ContinueStatement([14])
}
goto LL6
LL5: //None
LL6:
printf("%d", _t17);  // PrintStatement(LocationLookup([18] Var([17] n)))
_t23 = _t20 > 10;  // BinOp([23] >, LocationLookup([21] Var([20] n)), Integer([22] 10))
if (_t23) goto LL7; // IfConditional([26] BinOp([23] >, LocationLookup([21] Var([20] n)), Integer([22] 10)), Statements([25] Break([24])))
goto LL8;
LL7: //Statements([25] Break([24]))
{
goto LL3;  // Break([24])
}
goto LL9
LL8: //None
LL9:
}goto LL1;
LL3:
_t30 = -1;  // UnaryOp([30] -, Integer([29] 1))
printf("%d", _t30);  // PrintStatement(UnaryOp([30] -, Integer([29] 1)))
}
