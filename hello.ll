; ModuleID = "hello"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"hello"() 
{
entry:
  %"x" = alloca i32
  %"y" = alloca i32
  store i32 4, i32* %"x"
  store i32 5, i32* %"y"
  %".4" = load i32, i32* %"x"
  %".5" = mul i32 %".4", %".4"
  %".6" = load i32, i32* %"y"
  %".7" = mul i32 %".6", %".6"
  %".8" = add i32 %".5", %".7"
  %"d" = alloca i32
  store i32 %".8", i32* %"d"
  %".10" = load i32, i32* %"d"
  ret i32 %".10"
}

define double @"dsquared"(double %".1", double %".2") 
{
entry:
  %".4" = fmul double %".1", %".1"
  %".5" = fmul double %".2", %".2"
  %".6" = fadd double %".4", %".5"
  ret double %".6"
}

