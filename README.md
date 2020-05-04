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
 
## Live Session Recordings

Video recordings of live sessions will be posted here.

**Day 1**

* [Course Start, Project Demo](https://vimeo.com/414833210/68fdd7ea4a) (36 min)
* [Wabbit Language, Project 1](https://vimeo.com/414844050/552c0dd4e8) (45 min)
* [Project 1, Model Building](https://vimeo.com/414916917/186ecaa29e) (33 min)
* [Project 1, Day End](https://vimeo.com/414947839/c0184b46bd) (47 min)



