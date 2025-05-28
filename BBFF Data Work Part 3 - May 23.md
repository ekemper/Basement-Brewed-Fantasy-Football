BBFF Data Work Part 3 - May 23








20:22 - Mikey Henninger (Basement Brewed Fantasy Football)
  So the game data itself, it's valuable for me right now just from those projects that I'm talking about. But for what you're doing, you probably don't need to do anything with that until, like, August.  And even that is probably too early. September is probably the best. Now, what I will say is if you're able to get...  This is all the game information. If you're able to get the... Hold on. Sorry. I'm about to sidetrack it on accident.


20:56 - Mikey Henninger (Basement Brewed Fantasy Football)
  Go ahead. The player... You're going to find... Two different pieces of data for players. There is their season-long prop bets, so like, if you go in, you'll be able to see, is Saquon Barkley going to run for over 1,500 yards this year, as opposed to what you're currently looking at, which is like, in game one, is he going to run for 100 yards?


21:20 - Mikey Henninger (Basement Brewed Fantasy Football)
  If there was a way to have the season-long data on the specific players, that would be really valuable, even if it's refreshed once every two weeks or week or something like that.  But I don't know if that's something you're gathering in this process, because it's not, the season-long stuff isn't necessarily relevant to the heat map stuff, so it's kind of a different thing.  I don't know if you're gathering that or not.

21:48 - Eddie Kemper (getsmartscalingai.com)
  I don't think that's in the specific DraftKings stuff that I'm gathering now, but if it's just another page, we can always do it.  Okay. And especially once we have the infrastructure. Structure set up to organize that time domain information, we can always just start new scripts to scrape new data points.


23:12 - Eddie Kemper (getsmartscalingai.com)
  Okay. What I'd like to do is look at... Let me grab an actual heat map and put that up.  And... Let's see, probably this one's fine. And... We go here. Last time we talked about essentially these fields with this data, and that's what I'm gathering from DraftKings.  This set of data in these columns was what you were getting from or deriving from the defense and offense workbooks.

23:59 - Mikey Henninger (Basement Brewed Fantasy Football)
  Is that correct? Yep, so that specifically came from the defensive workbook. Yep, did I share that with you, the actual workbook?




27:19 - Mikey Henninger (Basement Brewed Fantasy Football)
  I honestly don't remember which one it is, but you can click on, this is the one. Yeah, raw player data.  So this is, I copy and paste into here. This literally shows every offensive player's box score against the team that they're, so like that top one, A.J.  Brown, he is on the Philadelphia Eagles. His opponent is the Green Bay Packers in that case. So this workbook registers all of his stats.  So if you scroll over, he had, what, 10 targets, 5 catches, 119 yards, 1 touchdown, 22.9 PPR points. It registers all of those numbers.  Under, the Green Bay Packers allowed this from that position. So A.J. Brown's a wide receiver, so it registered all of those numbers under wide receiver for the Packers, okay?  And then eventually it totals all of that for all of these teams and shows ranking one out of 32, this team allows either the most or the 32nd most, a.k.a.  fewest, PPR points per game to this specific position.


28:47 - Eddie Kemper (getsmartscalingai.com)
  Let me mirror it back to you and we'll iterate. So you get the raw player data and we'll go and figure out where to get this on the website.  But so A.J. Brown's a wide Receiver, and he's playing against Green Bay, and so PPR points, can you define PPR for me again?

29:08 - Mikey Henninger (Basement Brewed Fantasy Football)
  So PPR points is how it all, the sum of everything that happens. So I'll tell you, so if you look at column P, receptions, he had five catches.  Each catch is worth one point, okay? So he had five points there. The next one over is receiving yards.  You get one point for every 10 yards. So he had 11.9 yards there, and then the next one over is touchdowns, and you get six points for every one touchdown.  So PPR, that's the sum of those, all of those things combined. Now, obviously, there's, like, if you look down at Aaron Rodgers, it's different scoring for quarterback.  Like, it's not different scoring for the position, but each stat is different.

29:54 - Eddie Kemper (getsmartscalingai.com)
  Passing yards is different than rushing yards and all that stuff, but, yeah. Okay.

29:59 - Mikey Henninger (Basement Brewed Fantasy Football)
  Got it. Ultimately, when you go back to the all thing, this, yeah, these are ranking the PPR points. So it's the cumulative, the sum, it's ranking that.  It's not ranking like catches, it's not ranking yards. Until you look at, if you click all versus wide receiver, there you will see in column like, oh, that is showing, these are receptions.  now it's showing teams tend to give up the most receptions or less receptions, which is also valuable data. When I can, like, PPR points is helpful, but if I can drill, are they giving up a ton of PPR points because they're scoring a ton of touchdowns or catches or yards?  What is it? So all of this is helpful in its own way, but the numbers that you're looking for right now on the heat map, that is just the key.  Simulative PPR number and ranked. So it's ranked 1 through 32.

31:06 - Eddie Kemper (getsmartscalingai.com)
  32. Gotcha. That's great. Okay, so, yeah, let me mirror that back just so I can catch any misunderstanding. So if I go to AJ Brown, in order to get to this PPR point total, we're going to give six points per touchdown plus one point per 10 yards receiving, and then one point per reception, correct?

31:40 - Mikey Henninger (Basement Brewed Fantasy Football)
  Correct, yep.

31:41 - Eddie Kemper (getsmartscalingai.com)
  So that gives 22.9 for that particular game. We want to get all of, so that data, 22.9, is going to be utilized in Green Bay wide receiver.  Uh, stats.

32:02 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yep. Yep. And they gave up that production to wide receivers.

32:08 - Eddie Kemper (getsmartscalingai.com)
  Yep. Yeah. And so this is about this ranking for wide receivers. So wide receiver PPR points against Green Bay was accumulated across all of the wide receivers in that game.

32:28 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yep.

32:28 - Eddie Kemper (getsmartscalingai.com)
  Okay. And so, and that, that accounts for the different types of points that can be, uh, PPR points that can be used for a wide receiver.

32:42 - Mikey Henninger (Basement Brewed Fantasy Football)
  So reception yards, uh, reception count, and then touchdowns.

32:47 - Eddie Kemper (getsmartscalingai.com)
  Um, obviously there's different types of points accrued for different positions because they're involved in different types of plays.

32:57 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yep.

32:59 - Eddie Kemper (getsmartscalingai.com)
  And And Thank So the rankings for each of those different positions against each of those teams is accrued in each of those columns.

33:09 - Mikey Henninger (Basement Brewed Fantasy Football)
  Correct.

33:10 - Eddie Kemper (getsmartscalingai.com)
  And then we rank them per team.

33:13 - Mikey Henninger (Basement Brewed Fantasy Football)
  Rank them per team. Now, the one tiny caveat there is that we, if I recall correctly, because it's been a couple years now, but we set it up where it only, it finds a way to, how do I explain this?  So wide receivers, 99% of their points come from catches, yards, touchdowns, those three things. Now, every once in a while, a wide receiver will do something crazy, like they'll throw a touchdown pass, or they'll come around and they'll actually get a handoff, and they'll run that 99 yards, and those aren't receiving yards, those are rushing yards.  So we, I don't find those numbers helpful. It comes to predicting, like if the Packers give up a 99-yard rush to a wide receiver, that doesn't, that's going to make them look worse against wide receivers than they actually are.  Truth is, they just got beat on some weird, random, broken play that's not predictable in fantasy football. So anyways, my point is, these numbers that we're looking at right now, wide receivers and tight ends, I would only really want to focus on the normal stuff.  Catches, yards, touchdowns. Running backs are different. That would be rushing yards, receiving yards, touchdowns, catches. Quarterbacks, just passing yards, touchdowns, interceptions.  But anyway, I would only want to focus on what's common for that position, if that makes sense. That makes sense.

34:45 - Eddie Kemper (getsmartscalingai.com)
  Yep. Let me just check real quick. So here, each of these all versus wide receivers, running backs, tight ends, quarterbacks, these are the types of, this indicates.  It's each type of play which yields a PPR point, correct, or points. So the reception, reception yards, reception touchdowns.

35:12 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yep.

35:13 - Eddie Kemper (getsmartscalingai.com)
  And this is...

35:15 - Mikey Henninger (Basement Brewed Fantasy Football)
  And there's some of them that tell a really good story. Like if you look at Denver, for example, row 11, they...  So column AI, I think that is, which is kind of ironic. That's funny. That's ranked 22. So that tells us they're 22nd against wide receivers.  That's pretty tough. That's pretty good. They're the 11th best defense when it comes to wide receivers. But if you look at the specifics of that row, that is because they are allowing the fewest touchdowns.  Nobody is scoring touchdowns against them, right? That 0.67 number. But, Eddie, do you remember when we were talking about the Chiefs Raiders last week?

36:00 - Eddie Kemper (getsmartscalingai.com)
  They're the Raiders aren't going to score a lot of points, but they're going to throw a shitload of passes.  Yeah.

36:04 - Mikey Henninger (Basement Brewed Fantasy Football)
  This is where something like that could come in handy because, okay, the Broncos aren't allowing a lot of touchdowns, but they're allowing the ninth most catches and the eighth most receiving yards.  If they were playing, say, the Raiders in that example, we're not expecting the Raiders to score a lot of touchdowns anyway.  They can butter their bread on catches and yards. That's valuable information. So if a fantasy football player looks at just the raw number and says, oh, , the Broncos are holding wide receivers to the 11th fewest PPR points per game, that sucks.  If you go one step deeper as a fantasy football player, you can say, wait a minute, they're also giving up the ninth most catches, the eighth most receiving yards.  There's an opportunity for fantasy points. Don't just take the raw number and call it a day.

36:49 - Eddie Kemper (getsmartscalingai.com)
  I don't know if that made any sense, but that's why I want to dig into the nitty gritty so often is because you can still tell a story with some of these things.  Absolutely. Yeah, that's the kind of analysis. So I need to dig into you in order to create the correct prompts for this kind of stuff.  So let me bring that back. So Denver, for receiving touchdowns, since they have a low number, .67, that means they are tough on wide receivers and don't allow very many touchdown receptions for wide receivers.

37:34 - Mikey Henninger (Basement Brewed Fantasy Football)
  Two wide receivers, yeah.

37:36 - Eddie Kemper (getsmartscalingai.com)
  And if that were – so if Denver were playing a game against a team that was projected to – hold on.  So if Denver were playing a team against whom they would want...


38:16 - Eddie Kemper (getsmartscalingai.com)
  I'm there. I'm almost there. So if Denver were playing a game against a team that they knew they were going to throw, whether the opposing team was going to throw the ball a lot, you would know, based on this information, that Denver was going to be tough against wide receivers.  And in that game, you maybe wouldn't play a wide receiver against Denver in your league.


38:48 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yeah, so I think a good way to think about it is there are some wide receivers in football that get a lot of fantasy points because they score a lot of touchdowns.  So, like, there's a guy named... Mike Evans, he might only catch four or five passes in a game, but they're usually high leverage, high opportunity.  Like he scores, he gets 10 plus touchdowns a year, which is pretty good. In a game like this, or against a defense like Denver, Mike Evans might struggle.  Because they give up catches, but not touchdowns. Mike Evans doesn't get catches, he gets touchdowns. So that could be a struggle for Mike Evans.  Meanwhile, he has a teammate named Chris Godwin, who's the opposite. Chris Godwin gets like nine, 10 catches a game.  He just doesn't score a lot of touchdowns. So this game would be a good setup for, theoretically, it would be a good setup for Chris Godwin, right?  Because if the Broncos give up a ton of catches in yards, that's how Chris Godwin butters his bread. If the Broncos hold touchdowns, this could be a trap for Mike Evans.  And that's the story that I try and tell him the heat map is, hey. Hey. Usually you want to use Mike Evans, but beware, because what Mike Evans is good at, just so happens to be what the Broncos are good at stopping.  Right. Meanwhile, what Chris Godwin is good at, is where the Broncos suck, so Chris Godwin could go crazy.

40:18 - Eddie Kemper (getsmartscalingai.com)
  You know what I mean?

40:19 - Mikey Henninger (Basement Brewed Fantasy Football)
  So it's like, this stuff is like, that's why I always want to go just one step deeper, because people will stop at that raw number.  They'll see that 22 under FP rank. They'll see, oh, the Broncos hold wide receivers to the 11th fewest. don't want to use Chris Godwin, because they're tough on wide receivers.  Well, hold on a minute. If you drill just a little bit deeper, you'll see that this could actually set up pretty well for Chris Godwin.

40:44 - Eddie Kemper (getsmartscalingai.com)
  You know what I mean? Yeah, yeah. Okay. So I'm going to mirror that back just real quick.

40:51 - Mikey Henninger (Basement Brewed Fantasy Football)
  So in order to max, if I'm going to play, deciding whether to play a certain player, in a given game.

41:00 - Eddie Kemper (getsmartscalingai.com)
  With two specific teams, I want to match the strengths of my player against the team that are going to be opposing that player, and look for the opposing team's weaknesses.  Such that, for instance, if Chris Godwin is my player, I want to play that person against Denver, because that wide receiver is going to be catching and getting reception yards, but not necessarily touchdowns, because Denver is good at stopping specifically touchdown receptions against wide receivers.  But they might allow yardage and reception yardage and actual reception for wide receivers, and that's the strength of Chris Edmonds.  Chris. Chris Godwin, yep. Yep, and then Evans was the touchdown guy.

42:04 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yep, Mike Evans touchdowns, Godwin catches, yeah.

42:08 - Eddie Kemper (getsmartscalingai.com)
  Gotcha, okay.

42:09 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yep, I think you nailed it. And there's, like, if you look, there's a lot of these where, like Atlanta, Atlanta just straight up sucks.  Like, they'll, like, it doesn't matter who you're, just play your wide receiver against them, because they give up a ton of catches, a ton of yards, a ton of touchdowns.  And Chicago, on the other hand, they're just tough across the board. You don't want to use your wide receiver against them if you don't have to, because they shut down wide receivers.  But teams like Denver, that tells, or even right below them, Detroit, right, they give up a ton of catches, a ton of yards, not a lot of touchdowns.  And there's other areas where you'll find the exact opposite, where they give up touchdowns, but not a lot of catches.  So most of the time, it's going to be pretty consistent for most teams, or it won't be a screaming number in any way.  It'll be, like, average, right? 12, 13, 14. That doesn't really. Tell us anything good or bad, but sometimes you get a team like Denver where it's like, hold on, let's drill just a little bit deeper.  But yeah, you nailed it. If you're a fantasy football player, you want to know that, okay, if you're considering playing a wide receiver against the Denver Broncos, just understand it's probably not going to come from touchdowns.  You need it to come from catches and yards. So evaluate in your own mind whether or not your wide receiver is a guy that gets a lot of catches or if he's a guy who needs touchdowns to be successful.

43:34 - Eddie Kemper (getsmartscalingai.com)
  Right, right, right. Awesome. And so from raw player data, I will be able to ascertain those specific values as well.  So like if I go to, here's this guy, or this particular game, receptions, receiving... Or it's no touchdowns.

44:01 - Mikey Henninger (Basement Brewed Fantasy Football)
  Now, again, this one game, this isn't maybe, you know, several games. Just keep in mind, he's a running back, too.

44:08 - Eddie Kemper (getsmartscalingai.com)
  So he'll, so running backs do catch passes, but their bread and butter usually comes from rushing attempts.

44:15 - Mikey Henninger (Basement Brewed Fantasy Football)
  Rushing.

44:15 - Eddie Kemper (getsmartscalingai.com)
  Yeah, there we go. Okay, yeah, so. Okay. Yeah, a lot of good layers here.

44:26 - Mikey Henninger (Basement Brewed Fantasy Football)
  Okay. Okay.

44:27 - Eddie Kemper (getsmartscalingai.com)
  Yeah. So. In order to create. Prompts. For. Analysis of this data. I want to look at these totals and these rankings for each of these positions, but then also for each of those games go in and analyze the strengths and weaknesses.  Of the players and the team that they will be opposing, and in each case, and then take into account how those strengths and weaknesses match up for that particular player and that particular game.

45:18 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yep. So the stuff that we were just talking about with Mike Evans and Chris Godwin, that's where the player profile comes in handy.

45:27 - Eddie Kemper (getsmartscalingai.com)
  Okay.

45:28 - Mikey Henninger (Basement Brewed Fantasy Football)
  Your initial question for me, so this is my fault for pushing you down the player profile route, is under the QBRB wide receiver, the part you have highlighted right now, that is just a quick snapshot of PPR points allowed to each position.  So that'll just be a total number. It's the nitty gritty that we just dug into with Denver is specific to player profiles.

45:55 - Eddie Kemper (getsmartscalingai.com)
  Right, right. And so, but yeah, in general, I want to go in... Developing the prompts that are going to end up with the game script and the summaries for the players, I want to go deeper than just these totals, where I'm actually considering the strengths and weaknesses of players and the strengths and weaknesses of the teams that they're opposing for each game and each player.  Totally. Okay, that makes sense. And then, let's see, what's next? Maybe let's go, if I go back here, this is the raw player data, and all of that aggregates into these sheets, and then the totals, the fantasy point ranking goes to here for each particular position.

46:54 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yeah, and I'll be honest, in this particular moment, I am not remembering if it's... The raw player data that aggregates into there, or if it's the raw team data.  Now I'm thinking it might be the raw team data. If you want to pop that one open real quick, so I can just get a refresher on what raw team.  This is probably what it's using to populate the all numbers. Ah, yes it is, because if you look over columns, O, P, Q, R, S, T, that's when it gets position specific.  Because, and here I'll just try and say this real quick, those first 10 columns or whatever, A through L, M, whatever, those are just going to be the overall numbers that a team have given up just in general.  So like, the Arizona Cardinals may have given up, let's just, in column J, 3,912 receiving yards. But those could have gone to running backs, wide receivers, tight ends.  That doesn't necessarily help us, because if they're giving up a shitload of production to tight ends, that is important to know.  So that's where I, when you get into those later columns, you want to dig into, like, what have they given up wide receiver-specific, quarterback-specific.  So that information might be coming from raw player data. So either way, think player data is going to be what we want there.  But I might, I wish I could remember off the top of my head.

48:35 - Eddie Kemper (getsmartscalingai.com)
  Okay, that makes sense. Those are aggregated. And so, games played. This is throughout the entire season. Yep. So if I'm gathering this data, like, mid-season, I'm going to have maybe eight games played, and that'll be all.  All of these stats will be aggregated across the games that that team has played. Yep. And so, again, we're coming back to eventually time series data where I want to know, like, I can envision a world where, let's see, what is this?  The, oh, it won't let me drag it in.

49:25 - Mikey Henninger (Basement Brewed Fantasy Football)
  Why not? That's got to be tight end.

49:28 - Eddie Kemper (getsmartscalingai.com)
  Well, TE is tight end.

49:29 - Mikey Henninger (Basement Brewed Fantasy Football)
  Fantasy points. Fantasy points, probably, yeah.

49:32 - Eddie Kemper (getsmartscalingai.com)
  Or a fantasy yard.

49:33 - Mikey Henninger (Basement Brewed Fantasy Football)
  That's probably yards. No, it's FP, so that's fantasy points. Tight ends don't score a lot.

49:40 - Eddie Kemper (getsmartscalingai.com)
  That's why it's low. Okay. So, but I can imagine for each of these rows, in each of these columns, developing a time series graph that shows, okay, during the initial part of the season, Arizona was really hard on tight end.  And then somehow they started scoring a lot of points, you know?

50:04 - Mikey Henninger (Basement Brewed Fantasy Football)
  I don't know how much, how is that useful? Or is that the sort of... Not only is that useful, Edward, that is something I've been trying.  I don't even know if your real government name is Edward, but it just felt right in the moment. Not only is that useful, that is something that I've been wanting to get for a while.  That's something that we try to, if you look down at that raw weekly data, you'll see some graphs. Apps that start to show...  Oh, I thought it was in there. Maybe not. It must be in defense rankings or... Oh, defense trends.

50:38 - Eddie Kemper (getsmartscalingai.com)
  If you click on that one, I tried to get it, but I didn't...

50:43 - Mikey Henninger (Basement Brewed Fantasy Football)
  I couldn't understand what the hell I was looking at. So, because it just automatically populated and eventually I was like, what is this saying?  And I kind of gave up on it. But yes, to answer your question, that is something I would... Because that does happen.  And I currently don't have a good way of capturing that. Where there might be a team that is absolute dogshit against wide receivers for the first 10 games, and then suddenly they catch fire, and they're strong against wide receivers over the last six games.  And then you get into the fantasy football playoffs, and that is vital information to have, but I don't have a good way of capturing that.

51:18 - Eddie Kemper (getsmartscalingai.com)
  So, yes, if we had a time graph, that would be huge. Okay, so to review that, as the season progresses for each team, for each position, we want to be able to capture the metrics for each of those positions in terms of the different types of points from different types of plays, as well as the rankings for those positions against each of those teams, over time.

51:56 - Mikey Henninger (Basement Brewed Fantasy Football)
  And large... The rankings are... Definitely, definitely helpful, but even if not, even if, like, there's a way of showing, like, hey, over the first 10 games, the Detroit Lions were giving up 60 points per game to wide receivers, but now over the last six, they're only giving up 41 points per game, like, whatever.  I'm open to different ways of showing that, but yeah, rankings are definitely helpful.

52:23 - Eddie Kemper (getsmartscalingai.com)
  Okay. Okay, we're gonna have to review that, but I can put some thought into how that works, and that is not, that's not version one or even version two, but that will be helpful.  Yep. It's 9.30, let's just do a gut check.


52:51 - Eddie Kemper (getsmartscalingai.com)
  Sweet. Okay, so now, what I'd like to do, we have this raw player data, this is the data that comes  And on a weekly basis for or from the Python script that you have, what I'd like to do is gather this raw data from a website.

53:16 - Mikey Henninger (Basement Brewed Fantasy Football)
  I dropped in the chat the specific website that we use to gather this. It's come from football guys. They have a really helpful page called Game Logs Against.  So this is like if you pop that open. So this is showing you Arizona Cardinals against quarterbacks every game last year.  And then in 2025, it'll be one game at a time. And if you scroll down, it's going to show you what running backs did.  And this is why it's super helpful to know specifically what running backs did, what quarterbacks did, as opposed to just looking at a team total of the Cardinals have allowed X amount of rushing yards.  Well, rushing yards can come from quarterbacks and wide receivers.

53:59 - Eddie Kemper (getsmartscalingai.com)
  I want to know. That running backs have done.

54:03 - Mikey Henninger (Basement Brewed Fantasy Football)
  So, yeah, anyway, that's the website we've used in the past. Yeah.

54:11 - Eddie Kemper (getsmartscalingai.com)
  I'll leave it at that. And so, just looking at this real quick. These are running backs versus Aaron Zemmler.  Yeah. So, rushing plays, attempts, rushing yards, rushing touchdowns.

54:34 - Mikey Henninger (Basement Brewed Fantasy Football)
  The ball was thrown at them.

54:36 - Eddie Kemper (getsmartscalingai.com)
  It might not have caught it, but. Gotcha. So, targets are passes and receptions are the passes that were caught.

54:49 - Mikey Henninger (Basement Brewed Fantasy Football)
  Reception yards, reception touchdowns. Mm-hmm.

54:54 - Eddie Kemper (getsmartscalingai.com)
  Awesome. Okay. And then that gets collated into. No, going to go on. HeatNet, no. NFL Defense, raw player data.  Well, that would be raw team data, wouldn't it? Raw player.

55:13 - Mikey Henninger (Basement Brewed Fantasy Football)
  I mean, you can, I would say it's more raw player. That's definitely raw player data, because it's going show you each individual player, and then you can take those and sum them however.

55:27 - Eddie Kemper (getsmartscalingai.com)
  Oh, here it is.

55:34 - Mikey Henninger (Basement Brewed Fantasy Football)
  So, like, if you look down at the running backs, they, so that first week they played against Buffalo, so you're going to get individual box scores from all three of James Cook, Ray Davis, Ty Johnson.  Those are three Buffalo Bills running backs, so you can accumulate that into, like, the Buffalo running backs did, but then split it out at the individual level as well.  So, I don't know how that. I don't know if that's raw player data or raw team data, because that would show you, like, okay, James Cook plus Ray Davis plus Ty Johnson.  The Cardinals gave up, let's just say, 24 rushing attempts to Bill's running backs. So they've given up 24 rushing attempts to running backs, but now if you want to split it out individually, James Cook had 19, Ray Davis had 3, Ty Johnson had 2.

56:28 - Eddie Kemper (getsmartscalingai.com)
  Gotcha.

56:28 - Mikey Henninger (Basement Brewed Fantasy Football)
  I don't know if I just made that confusing.

56:31 - Eddie Kemper (getsmartscalingai.com)
  Nope, that makes sense. Okay, and so if I scrape this data, I can reproduce the defensive player spreadsheet, which then is aggregated into the per position fantasy point sheet, and then further aggregated into the totals for...  For each position against specific teams. And then all of that for a weekly heat map, all of that information would be aggregated into the previous weeks in the season that led up to that game.

57:17 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yep.

57:19 - Eddie Kemper (getsmartscalingai.com)
  Perfect. Okay, I can do that. Now, that covers the data. For that particular chunk. And I don't want to go any deeper into more data right now because that's already enough for me to chew on.

57:38 - Mikey Henninger (Basement Brewed Fantasy Football)
  Sure, I get that.

57:43 - Eddie Kemper (getsmartscalingai.com)
  But, in terms of prompting, I want to come back to this idea of comparing the strengths and weaknesses of each team against the strengths and weaknesses of the players across each of these positions.  Thank To predict a specific analytical result for each player in that game, across quarterbacks, right receivers, running backs, tight ends.  Okay, I like that. That's good. Um, that's enough. I think I'm going to chew on that for a day or so, and that'll get me down the road.

58:34 - Mikey Henninger (Basement Brewed Fantasy Football)
  Can I throw one?

58:36 - Eddie Kemper (getsmartscalingai.com)
  Yeah, go for it.

58:37 - Mikey Henninger (Basement Brewed Fantasy Football)
  Quick curveball at you?

58:39 - Eddie Kemper (getsmartscalingai.com)
  Yeah.

58:40 - Mikey Henninger (Basement Brewed Fantasy Football)
  Totally fine with everything that we have already discussed, if that's the route you want to go. Otherwise, I just dropped another link in the chat, if you can pop that one open real quick.  This is just a, another potential. Data Source, if you like this better than Football Guys, because let's just stick with Arizona Cardinals.  That's what we've been doing, right? So right now you're on the week one of last year. If you go four games over to the right on the Arizona Cardinals Buffalo Bills, if you click final, that should...  Yeah, perfect. All right, and then you scroll down. This is going to give you, I think, all of the same data and then some.  So if you keep scrolling down, keep going, it's going to show you all that stuff, which is cool. But if you keep going down, it'll eventually get to, should at least, like passing, rushing, receive.


59:48 - Mikey Henninger (Basement Brewed Fantasy Football)
  Now, the only difference is this is just showing both teams' offenses. So it's not saying, like the other page that you were on said, Arizona against Buffalo.  Oh, well, thank you. This is just saying, here's what Arizona did, here's what Buffalo did. So, like, theoretically, you would have to find a way to attribute, do you know what I'm saying?  Like, you would have to make the data say, Arizona allowed all these box scores to Buffalo.


1:00:27 - Mikey Henninger (Basement Brewed Fantasy Football)
  Yeah, so, I don't know how to explain this. So, you go back, like, if you look at the game logs thing on Football Guys at the top, your third tab on your browser, this is saying, like, this is an Arizona Cardinals page that you're on.  Yeah. But none of this has anything to do with the Cardinals.

1:00:48 - Eddie Kemper (getsmartscalingai.com)
  It's showing what their opponents have done, right?

1:00:50 - Mikey Henninger (Basement Brewed Fantasy Football)
  Right. These are the Cardinals, here's their opponents. Now, if you go back to what we were just, that first tab, Arizona Cardinals at Buffalo.  Yeah. Bills, this is just showing the overall box score. This is just saying Cardinals, Bills, here's what the Cardinals did on offense, here's what the Bills did on offense.  So you would have to set up the sheet somehow to identify, oh, the Cardinals played in this game, and their opponent was the Buffalo Bills, so these are the stats we need to grab, that sort of thing.  So I'm wondering, the only reason I even brought this whole other website up, Eddie, is because I think I have noticed in the past that they bring even more data to the table that could eventually be helpful down the road, whereas Football Guys has just the basic catches, yards, touchdowns, which is totally cool.  Like, I'm totally fine with sticking with that. I just didn't know if we were starting from scratch, pulling data from somewhere, should we start pulling data from Pro Football Reference, because they usually have, like, just an absurd amount of data in here, but I'm totally fine with...

1:02:00 - Eddie Kemper (getsmartscalingai.com)
  Let's use the more robust data set, but what I would want to ask is which data points beyond what we're looking at with football guys would you be interested in in order to drive the analysis for either the game script or the player script?

1:02:23 - Mikey Henninger (Basement Brewed Fantasy Football)
  Can you say that again?

1:02:26 - Eddie Kemper (getsmartscalingai.com)
  So given that Pro Football Reference has more data, which additional data points beyond what we saw on football guys would you be interested in developing the player summaries or the game script?

1:02:45 - Mikey Henninger (Basement Brewed Fantasy Football)
  Um, game script? Probably nothing. It would come in for player summaries, and I don't have a set answer for you yet.  Um, uh, like... Something that I've cared about in the past, but I haven't found a good way to incorporate, is snap count, meaning how many plays a player is actually on the football field.  Some more advanced stuff, like wide receivers, for example. How many routes have they won? That's important. Like, what's their...  What was the other one I was literally... Oh, red zone stats. So, red zone means if they're inside the 20-yard line, they're close to scoring a touchdown.  There's a lot of teams that use very specific players in those situations because they're just good at, like, the Buccaneers.  If they get in the red zone, they're going to start looking at Mike Evans.

1:03:39 - Eddie Kemper (getsmartscalingai.com)
  The guy scores touchdowns. That's what he does.

1:03:41 - Mikey Henninger (Basement Brewed Fantasy Football)
  Got it. And those sorts of data and information are definitely helpful. However, I'm literally back on Football Guys right now.  So, you go the third tab in your browser, and if you look right under that... Arizona Cardinals drop down.  There's team red zone stats, there's team targets, there's snap counts. So I think it's probably just the sort of thing where I just wasn't pulling enough.  Like, it's here, I just don't think I was pulling enough data. So we might just be able to stick with football, guys.


1:04:44 - Eddie Kemper (getsmartscalingai.com)
  Okay. Are there, within the context of the data and the analysis that we've been looking at, are there any other sort of heuristics or...  ... ... ... Interesting edge cases that you like to keep track of that might be helpful in this initial first pass.  We can always come back and kind of re-evaluate once I've got the data hooked up and the first pass of the player summary and game script.  And we can always add more data and more analysis. I think there'll be a few different passes here and really a few different iterations in getting to a point where each of those things feels complete from your perspective.  From where I'm standing, that's enough to get me going so that we have all the data for an initial player summary and all of the data for an initial game script.  But if there's anything else you want to add to that analysis at this point, we can listen to that now, too.


1:06:26 - Mikey Henninger (Basement Brewed Fantasy Football)
  Neither will be perfect or complete, but it'll be a first iteration. Um, no, I don't think there's anything specific I can think of.  It's always just the sort of thing where it's like, I'm trying to tell two stories, right? The first one is like, what does the game script tell us about how the game itself, before you even think about players, how will the game go?  And then from from there, it's... But now that we have a theory about how the game will go, what does that mean for player A, player B, player C, player D?  And for each one of those players, it might be a different story because each player has a different profile of where they get their fantasy points from.  So I'm thinking that just whatever we come up with as a first pass will probably influence whatever the second pass is.



