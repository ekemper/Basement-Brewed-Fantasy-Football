you are to create a plan for an ai agent to perform the following task:



in the following directory there are many csv files:

Basement-Brewed-Fantasy-Football/server/football_guys_scrapers/data/games_logs_against

each file name starts with a 3 letter code for the team. the middle part of the file name is the posiition.

the files contain data on how that partiular team performed against that position.

here is an example of the data ( ARI vs quarterbacks):


name,week,team,cmp,att,pyd,ptd,int,rsh,rshyd,rshtd
Josh Allen,1,BUF,18,23,232,2,0,9,39,2
Matthew Stafford,2,LAR,19,27,216,0,0,0,0,0
Jared Goff,3,DET,18,23,199,2,1,3,6,0
Jayden Daniels,4,WAS,26,30,233,1,1,8,47,1
Brock Purdy,5,SF,19,35,244,1,2,4,33,0
Jordan Love,6,GB,22,32,258,4,1,5,13,0
Justin Herbert,7,LAC,27,39,349,0,0,2,8,0
Tua Tagovailoa,8,MIA,28,38,234,1,0,3,13,0
Caleb Williams,9,CHI,22,41,217,0,0,4,5,0
Aaron Rodgers,10,NYJ,22,35,151,0,0,0,0,0
Geno Smith,12,SEA,22,31,254,1,1,3,2,0
Sam Darnold,13,MIN,21,31,235,2,0,4,22,0
Geno Smith,14,SEA,24,30,233,1,0,1,0,0
Drake Maye,15,NE,19,23,202,1,1,4,14,1
Bryce Young,16,CAR,17,26,158,2,0,5,68,1
Matthew Stafford,17,LAR,17,32,189,0,0,6,16,0
Joshua Dobbs,18,SF,29,43,326,2,2,8,17,1


There is a file for each team vs each position.

Our goal is to create a csv file for each position. ( quarterbacks, running backs, wide receivers, tight ends)
In each of these files we want aggrigated data for each team vs that position. The data from each player is aggregated into the team level.


The following files are the exact files that we want to create from our individual 'teams vs position' files.

/home/ek/dev/Basement-Brewed-Fantasy-Football/all-vs-TE.tsv
/home/ek/dev/Basement-Brewed-Fantasy-Football/all-vs-WR.tsv
/home/ek/dev/Basement-Brewed-Fantasy-Football/all-vs-RB.tsv
/home/ek/dev/Basement-Brewed-Fantasy-Football/all-vs-QB.tsv

plese ensure continuity for each of the columns that are aggrigated from the player level data.


For each of the aggrigate data columns, there are averages and the rank of the team against the other teams for that average. These values must be calculated from the aggrigated data columns.   

For all the testing, the all-vs-* files can be used to test the accuracy of the aggrigated data and the calculated values


notes: fantasy points are calculated as described in ppr-point-calculations.md

for this task:

pleaes create an extreamly detailed set of step by step instructions for an ai agent to perform the task

The instructions should break the process down in to discrete, testable steps.

Each step should have a clear goal, a clear set of actions to be performed by the ai agent, and a strategy for confirming that the actions were sucessfull.

In cases where there are code edits, the ai agent is to perform the changes.

In cases where there are commands to be run, the ai agent is to run them in the chat window context and parse the output for errors and other actionable information.

Be wary of over engineering things. If there is a simple way to do something that gets 80% of the value with 20% the complexity, opt for that implementation.


For the plan you create, please create a md document in the root of the project and put the instructions there for safe keeping








