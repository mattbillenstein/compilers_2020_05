@echo off
for %%a in (tests\Script\*.wb) do (
  echo %%a
  python3 -m wabbit.typecheck %%a
  )