

pleaes create an extreamly detailed set of step by step instructions for an ai agent to perform the following task:


## Objectives:

* Create a script to use the existing scrapers to create a spreadsheet with all of the same columns in the tsv sample. 
* Add the snapcount data to the spreadsheet
* Create a dedicated scraper module to extract that data and include it in the final csv
* Create a final spreadsheet with all the columns from the tsv sample with the exception of:

please create a script to use the existing scrapers to create a spreadsheet with all of the same columns in the tsv sample. 

additionally the snapcount data can be found here
@https://www.footballguys.com/stats/snap-counts/teams?team=ARI&year=2024 

please make a dedicated scraper module to extract that data and include it in the final csv

the final spread sheet should have all the columns from the tsv sample with the exception of:

PPR_Points & PPR_Average (can be calculated)

Reg_League_Avg & Reg_Due_For (advanced analytics)

please design the script so that data for all the players for all the games for  the whole 2024 season can be extracted


Here are some more general instructions:


The current patterns, conventions, and configuration for this app (fastapi-k8-proto) should be maintained at all cost.

The instructions should break the process down in to discrete, testable steps.

Each step should have a clear goal, a clear set of actions to be performed by the ai agent, and a strategy for confirming that the actions were sucessfull.

In cases where there are code edits, the ai agent is to perform the changes.

In cases where there are commands to be run, the ai agent is to run them in the chat window context and parse the output for errors and other actionable information.

Be wary of over engineering things. If there is a simple way to do something that gets 80% of the value with 20% the complexity, opt for that implementation.




For the plan you create, please create a md document in the root of the project and put the instructions there for safe keeping
