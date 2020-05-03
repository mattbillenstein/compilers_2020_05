# Compilation to a Standalone Executable

In the wiki, the following is given:

Compile this program together with hello.ll to make an executable:

```
bash % clang main.c hello.ll
bash % ./a.out
hello() returned 37
```

However, on Windows, the output file is a .exe file, and there is a warning given.

```
(base) C:\Users\andre\github\compilers_2020_05\llvm_tutorial>clang main.c hello.ll
warning: overriding the module target triple with x86_64-pc-windows-msvc19.16.27034 [-Woverride-module]
1 warning generated.

(base) C:\Users\andre\github\compilers_2020_05\llvm_tutorial>dir
 Le volume dans le lecteur C s’appelle Local Disk
 Le numéro de série du volume est 8085-52B5

 Répertoire de C:\Users\andre\github\compilers_2020_05\llvm_tutorial

2020-04-30  15:55    <DIR>          .
2020-04-30  15:55    <DIR>          ..
2020-04-30  15:55           119 296 a.exe
```

However, it still works "as expected".
