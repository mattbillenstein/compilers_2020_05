@echo off
for %%a in (tests\Script\*.wb) do python3 -m wabbit.typecheck %%a