# Write a Compiler : May 4-8, 2020

Hello! This is the course project repo for the "Write a Compiler"
course.  This project will serve as the central point of discussion, code
sharing, debugging, and other matters related to the compiler project.

Although each person will work on their own compiler, it is requested
that all participants work from this central project, but in a separate
branch.   You'll perform these setup steps:

    bash % git clone https://github.com/dabeaz/compilers_2020_05
    bash % cd compilers_2020_05
    bash % git checkout -b yourname
    bash % git push -u origin yourname

There are a couple of thought on this approach. First, it makes it
easier for me to look at your code and answer questions (you can 
point me at your code, raise an issue, etc.).   It also makes it easier
for everyone else to look at your code and to get ideas.  Writing a
compiler is difficult. Everyone is going to have different ideas about
the implementation, testing, and other matters.  By having all of the
code in one place and in different branches, it will be better.

I will also be using the repo to commit materials, solutions, and 
other things as the course nears and during the course.

Finally, the repo serves as a good historical record for everything
that happened during the course after the fact.

Best,
Dave

## Important Note

Everything in this repo is subject to change up until the course start date.
Free feel to look around now, but you may want to check back from time to
time to see what's new.

## Live Session 

The course is conducted live from 09:30 to 17:30 US Central Time on Zoom.
The meeting will be open about 30 minutes prior to the starttime. Meeting
details are as follows:

Topic: Write a Compiler, May 4-8, 2020.
Time: 09:00 - 18:00 US CDT (UTC-05:00). 

Join Zoom Meeting
https://us02web.zoom.us/j/82940491798?pwd=U05FZ1FIZHhTeWNWbitkWlNOOFk3Zz09

Meeting ID: 829 4049 1798.
Password: 016509.

## Course Requirements

Here are some of the basic software requirements:

* Python 3.6 or newer.
* llvmlite
* Clang C/C++ compiler.

One easy way to get llvmlite is to install the Anaconda Python
distribution.  If you intend to write a compiler in a different
language than Python, you will need to investigate the availability of
tools for generating LLVM. There is probably some library similar to
llvmlite.

## Resources

* [Documents & Wiki](https://github.com/dabeaz/compilers_2020_05/wiki)

## Warmup work

If you're looking to get started, there are some warmup exercises posted
on the wiki.   Reposted here.

* [Warmup Exercises](https://github.com/dabeaz/compilers_2020_05/wiki/Warmup-Exercises)
* [Recursion Exercises](https://github.com/dabeaz/compilers_2020_05/wiki/Recursion-Exercises)
* [Project 0 - The Metal](https://github.com/dabeaz/compilers_2020_05/wiki/Project-0---The-Metal)
* [Project 0.5 - SillyWabbit](https://github.com/dabeaz/compilers_2020_05/wiki/Project-0.5---SillyWabbit)

## Videos

Short video lectures will introduce important parts of the project.  They will be posted here
about a day in advance (an email notification will also be sent).

* [Course Introduction](https://vimeo.com/414481789/f5cc08e05b) (20 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/00Compiler.pdf) 
* [Part 0 - Preliminaries](https://vimeo.com/414482511/54dff477c1) (7 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/00Preliminaries.pdf)
* [Part 1 - Structure of Programs](https://vimeo.com/414482772/bcf107cae6) (9 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/01Structure.pdf)
* [Part 2 - Evaluation of Programs](https://vimeo.com/414763523/fb21573130) (11 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/02Evaluation.pdf)
* [Part 3 - Lexing](https://github.com/dabeaz/compilers_2020_05/raw/master/present/03Lexing.pdf) (PDF)
* [Part 4 - Parsing](https://vimeo.com/414973515/c64a69c8bb) (26 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/04Parsing.pdf)
* [Part 5 - Type Checking](https://vimeo.com/415496010/c8a7d880fd) (13 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/05TypeChecking.pdf) 
* [Part 6 - Code Generation](https://vimeo.com/415496570/329760928e) (11 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/06CodeGeneration.pdf) 
* [Part 7 - Transformations](https://vimeo.com/415915433/c7b6db33fd) (5 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/07Transformations.pdf) 
* [Part 8 - Intermediate Code](https://vimeo.com/415915651/be16724fd6) (11 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/08IRCode.pdf) 
* [Part 9 - Functions](https://vimeo.com/416322374/7b280d972b) (20 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/09Functions.pdf) 
* [Part 10 - Advanced Types](https://vimeo.com/416321717/9907d0e2c0) (15 min) [PDF](https://github.com/dabeaz/compilers_2020_05/raw/master/present/10AdvancedTypes.pdf) 

## Live Session Recordings

Video recordings of live sessions will be posted here.

**Day 1**

* [Course Start, Project Demo](https://vimeo.com/414833210/68fdd7ea4a) (36 min)
* [Wabbit Language, Project 1](https://vimeo.com/414844050/552c0dd4e8) (45 min)
* [Project 1, Model Building](https://vimeo.com/414916917/186ecaa29e) (33 min)
* [Project 1, Day End](https://vimeo.com/414947839/c0184b46bd) (47 min)

**Day 2**

* [Project 2, Interpreter](https://vimeo.com/415255889/afc6ba5e32) (29 min)
* [Project 2, Interpreter - Continued](https://vimeo.com/415257318/24d5d31cd4) (33 min)
* [Project 2 End, Project 3 Start](https://vimeo.com/415258940/df543c3b50) (50 min)
* [Project 3, Tokenizing, Checkin](https://vimeo.com/415330823/8be50c609f) (11 min)
* [Project 4, Parsing Introduction](https://vimeo.com/415331200/7bee239ef9) (95 min)

**Day 3**

* [Project 4, Parsing in Practice](https://vimeo.com/415631778/b3b3d1c157) (67 min)
* [Project 4, Parsing, errors, precedence](https://vimeo.com/415636966/f82ce24e02) (38 min)
* [Project 5, Type Checking](https://vimeo.com/415678414/d87a14cb3f) (32 min)
* [Error Handling](https://vimeo.com/415917112/03bf76a938) (45 min)

**Day 4**

* [Project 6, Code Generation](https://vimeo.com/416163581/9641e7d260) (44 min)
* [Code generation](https://vimeo.com/416163359/5c018c29b3) (7 min)
* [Stacks and code generation](https://vimeo.com/416162660/5d7cf08715) (13 min)
* [WebAssembly discussion](https://vimeo.com/416159967/5550b1fb27) (56 min)

**Day 5**

* [Code generation, LLVM, functions](https://vimeo.com/416473824/a57d139059) (42 min)
* [Functions, JITs, discussion](https://vimeo.com/416473824/a57d139059) (56 min)
* [Near the end, discussion](https://vimeo.com/416531903/b8049251fe) (40 min)
* [End. Resource. Discussion](https://vimeo.com/416530895/e900197a10) (35 min)

