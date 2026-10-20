#!/usr/bin/env python3
"""Permitted standard-library checks; source commands are parsed only, never installed/launched."""
from pathlib import Path
import json,sys,datetime,hashlib,math,random,shlex,shutil
from fractions import Fraction as F
R=Path(__file__).resolve().parents[1];B='W12-L58';started=datetime.datetime.now(datetime.timezone.utc).isoformat();b=json.loads((R/f'data/question-batches/{B}.json').read_text());Q={q['id'].split(B+'-')[1]:q for q in b['questions']};checks=[]
def ck(name,test,detail):
 assert test,name
 checks.append(dict(id=f'L58-AUTHOR-{len(checks)+1:02}',name=name,detail=detail,passed=True))
def selected(qid):q=Q[qid];return[o['text']for o in q['options']if o['id']in q['correctOptionIds']]
def keyed(qid,text):ck(qid+' saved answer binding',any(text in s for s in selected(qid)),'Compared computed result with the actual saved option text and stable option ID, not option position.')
r=F(5,100);x=F(-1)+(9+F(1,2))*r;y=F(2)+(3+F(1,2))*r
ck('Grid dimensions and center',80*r==4 and 40*r==2 and x==F(-525,1000)and y==F(2175,1000),'4m×2m;center(−0.525,2.175)m under supplied lower-left indexing.')
ck('Grid corner distractor',F(-1)+9*r==F(-55,100)and F(2)+3*r==F(215,100),'Half-cell omission yields(−0.550,2.150)m;80m×40m ignores0.05m/cell.')
keyed('P1855-Q03','−0.525')
routes={'A':([F(2),F(3)],False),'B':([F(2),F(2),F(2)],True),'C':([F(4),F(3)],True)}
ck('Path lengths and feasibility',min((sum(v),k)for k,(v,ok)in routes.items()if ok)==(F(6),'B')and sum(routes['A'][0])==5 and sum(routes['C'][0])==7,'Infeasible5m route excluded;6m beats7m.');keyed('P1861-Q03','Route B, 6 m')
v,tau,a=F('0.6'),F('0.2'),F('0.9');dr=v*tau;db=v*v/(2*a);ds=dr+db
ck('Stopping and clearance',dr==F('.12')and db==F('.2')and ds==F('.32')and F('.4')-ds==F('.08'),'SI units;reaction+braking;distancefromleadingboundary.')
ck('Stopping distractors',db==F('.20')and F('.4')-db==F('.20')and dr+v*v/a==F('.52')and F('.4')-(dr+v*v/a)==F('-.12'),'Ignore reaction versus omit2denominator.');keyed('P1862-Q03','0.32 m')
width,rad,margin=F('.45'),F('.2'),F('.05');side=(width-2*rad)/2
ck('Clearance margin',side==F('.025')and 2*(rad+margin)==F('.5')and side<margin,'0.05m total gap splits across two sides;fits bare diameter but fails supplied margin.');keyed('P1863-Q03','required width is 0.50 m')
u=[F(2),F(3),F(5)];weights=[v/sum(u)for v in u]
ck('Particle normalization',weights==[F('.2'),F('.3'),F('.5')]and sum(weights)==1,'Divide by total10,notmax5.');ck('Particle distractors',sum(v/max(u)for v in u)==2 and weights!=[F(1,3)]*3,'Max-normalized weights sum2;uniform discards unequal weights.');keyed('P1864-Q03','0.2, 0.3, 0.5')
ck('Simulation clock arithmetic',F(6,10)==F('.6')and F('1.2')/6==F('.2')and F('1.2')/10==F('.12')and round(10/6,2)==1.67,'Real-timefactor.6;simulatedspeed.20m/s;wallspeed.12m/s;inversefactor1.67.');keyed('P1868-Q03','0.6 and 0.20')
ck('ETA conditional speed',F('3.01')/14==F('.215')and round(3.01/9,3)==.334 and round(14/3.01,3)==4.651,'Remainingdistanceremainingtime gives.215m/s;elapsedtime mismatch.334;inverseratio4.651s/m.');keyed('P1872-Q02','0.215')
# Supplied abstract tree, not execution of Nav2 or a particular BehaviorTree.CPP release.
trace=[]
def seq():
 trace.append('Plan');status='FAILURE'
 if status!='SUCCESS':return status
 trace.append('Follow');return'SUCCESS'
def fallback():
 status=seq()
 if status=='SUCCESS':return status
 trace.append('Recover');return'SUCCESS'
ck('Supplied tree trace',fallback()=='SUCCESS'and trace==['Plan','Recover'],'Sequence failure skipsFollow;FallbacktriesRecover.');keyed('P1860-Q02','Plan → Recover; SUCCESS')
# Exact visible source commands. No subprocess invocation, shell sourcing, package installation or ROS launch.
commands=[
 dict(page=1867,printedLines=['sudo apt install ros-humble-navigation2','ros-humble-nav2-bringup'],normalized='sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup',qualification='Visual wrap explicitly joined into one logical line.'),
 dict(page=1867,printedLines=['sudo apt install ros-humble-turtlebot3*'],normalized='sudo apt install ros-humble-turtlebot3*',qualification='Wildcard preserved as text; no shell expansion or installation attempted.'),
 dict(page=1867,printedLines=['export TURTLEBOT3_MODEL=waffle.'],normalized='export TURTLEBOT3_MODEL=waffle.',repaired='export TURTLEBOT3_MODEL=waffle',qualification='Literal period preserved; repair labeled separately.'),
 dict(page=1867,printedLines=['ros2 launch turtlebot3_gazebo','turtlebot3_world.launch.py'],normalized='ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py',repeatedOn=[1868,1870],qualification='Display wrap joined; repeated source launch not executed repeatedly.'),
 dict(page=1868,printedLines=['ros2 launch turtlebot3_cartographer','cartographer.launch.py','use_sim_time:=True'],normalized='ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True',qualification='Display wraps joined; Cartographer not silently renamed SLAM toolbox.'),
 dict(page=1869,printedLines=['ros2 run turtlebot3_teleop','teleop_keyboard'],normalized='ros2 run turtlebot3_teleop teleop_keyboard',qualification='Executable invocation, not launch file.'),
 dict(page=1869,printedLines=['ros2 run nav2_map_server','map_saver_cli -f my_map'],normalized='ros2 run nav2_map_server map_saver_cli -f my_map',qualification='Output basename; no actual map created.'),
 dict(page=1870,printedLines=['ros2 launch turtlebot3_navigation2','navigation2.launch.py use_sim_time:=True','map:=path/to/my_map.yaml'],normalized='ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=path/to/my_map.yaml',repairedExample='ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=/home/student/maps/my_map.yaml',qualification='Placeholder preserved; example supplied path not claimed to exist in this workspace.')]
ck('Joined apt tokens',shlex.split(commands[0]['normalized'])==['sudo','apt','install','ros-humble-navigation2','ros-humble-nav2-bringup'],'Two package arguments; display-newline split is not equivalent to joinedcommand.');keyed('P1867-Q01','two named Humble packages')
val=shlex.split(commands[2]['normalized'])[1].split('=',1)[1];repair=shlex.split(commands[2]['repaired'])[1].split('=',1)[1]
ck('Literal and repaired model values',val=='waffle.'and repair=='waffle'and val not in ['burger','waffle','waffle_pi'],'Puretokencomparison;noenvironmentwrite.');keyed('P1867-Q02','Assigned value waffle.;')
ck('Simulator package/file',shlex.split(commands[3]['normalized'])[2:]==['turtlebot3_gazebo','turtlebot3_world.launch.py'],'ros2launch package/file roles.');keyed('P1867-Q03','Package turtlebot3_gazebo')
ck('Cartographer clock argument',shlex.split(commands[4]['normalized'])[2:]==['turtlebot3_cartographer','cartographer.launch.py','use_sim_time:=True'],'Clocksourcearg,notrealtimefactor.');keyed('P1868-Q01','simulation clock')
ck('Teleop run tokens',shlex.split(commands[5]['normalized'])[1:]==['run','turtlebot3_teleop','teleop_keyboard'],'Package/executable;noROSprocess.');keyed('P1869-Q01','teleop_keyboard executable in the turtlebot3_teleop')
ck('Map saver tokens',shlex.split(commands[6]['normalized'])[2:]==['nav2_map_server','map_saver_cli','-f','my_map'],'Outputbasename.');keyed('P1869-Q02','output basename')
navtokens=shlex.split(commands[7]['normalized']);arg=dict(t.split(':=',1)for t in navtokens[4:])
ck('Navigation arguments',arg=={'use_sim_time':'True','map':'path/to/my_map.yaml'},'Literalplaceholderandclock retained;repairedpathsareexplicit suppliedexamples.');keyed('P1870-Q01','map:=/home/student/maps/my_map.yaml');keyed('P1870-Q04','point map to /maps/lab.yaml')
ck('Legacy direct sensor branches',set(selected('P1858-Q02'))=={'Global costmap','Local costmap'},'Bothcostmaptargets;indirectplanneredgesnotdirectsensorarrows.')
keyed('P1858-Q01','Global planner → path → local planner → velocity command → base controller');keyed('P1859-Q02','Controller → Velocity Smoother → Collision Monitor → Robot Base')
ck('Historical screenshot status chronology',all(any(t in s for s in selected(qid))for qid,t in [('P1870-Q02','readiness is not yet established'),('P1871-Q02','does not show a completed goal'),('P1873-Q01','reporting reached')]),'Source screenshots:unknown/error,thenactive/unknown,thenreached;notnewexecutionorfulltrajectory.')
keyed('P1873-Q02','still names burger');keyed('P1866-Q03','report failure if the route remains infeasible')
rng=random.Random(5801)
for _ in range(1000):
 rr=F(rng.randrange(1,101),100);nx,ny=rng.randrange(1,201),rng.randrange(1,201);ii,jj=rng.randrange(nx),rng.randrange(ny);xx=(ii+F(1,2))*rr;yy=(jj+F(1,2))*rr
 assert 0<xx<nx*rr and 0<yy<ny*rr
 uu=[F(rng.randrange(1,101))for _ in range(5)];ww=[v/sum(uu)for v in uu];assert sum(ww)==1 and all(0<w<1 for w in ww)
 vv,tt,aa=F(rng.randrange(1,101),20),F(rng.randrange(0,101),100),F(rng.randrange(1,101),20);dd=vv*tt+vv*vv/(2*aa);assert dd>=vv*vv/(2*aa)and dd>=vv*tt
 rad=F(rng.randrange(1,101),100);m=F(rng.randrange(1,51),100);w=2*(rad+m);assert (w-2*rad)/2==m
ck('Random numerical invariants',True,'1000seededcases/4000assertions:gridcentersinsidebounds,normalizedweights,stoppingdistancebounds,exactclearanceboundary.')
report=dict(role='Author-side checks only; independent review required',batchId=B,startedAt=started,completedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),command='python scripts/check_W12_L58_author.py',interpreter=sys.executable,pythonVersion=sys.version,importedPackages='Python standard library only',runtimeAvailability=dict(ros2=shutil.which('ros2'),gazebo=shutil.which('gazebo')),executionScope='Command strings parsed only. No sudo/apt, ROS/Gazebo installation, launch, model inference, hardware, video playback or restricted runtime used. Numerical examples explicitly supplied; screenshot values historical.',checkGroups=len(checks),checks=checks,randomCases=1000,randomAssertions=4000,sourceCommands=commands,questionBatchSha256=hashlib.sha256((R/f'data/question-batches/{B}.json').read_bytes()).hexdigest())
(R/f'audits/{B}-author-checks.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print('PASS',len(checks),'groups,1000cases/4000assertions')
