@echo off
for %%a in (tests\Script\*.wb) do (
  echo %%a
  python3 -m wabbit.c %%a
  wsl cc out.c

  )