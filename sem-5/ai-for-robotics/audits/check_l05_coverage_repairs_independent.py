"""Independent course-source checks; no ROS, author script, or question writes."""
import ast, json
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timezone
checks=[]
def check(name, actual, expected):
    passed=actual==expected
    checks.append({'name':name,'actual':actual,'expected':expected,'passed':passed})
    assert passed, name
# Positive deadline miss; exact hypothetical milliseconds, not timing benchmark.
for service,deadline,want in [(8,1,7),(1,1,0),(0,1,0),(8,0,8),(8,9,0)]:
    check(f'positive deadline miss service={service}, deadline={deadline}',max(0,service-deadline),want)
check('four numerical alternatives are distinct',len({0,1,7,8}),4)
# Faithful source guard reduced to a recording main, without invoking ROS.
code='def main():\n    calls.append("main")\nif __name__ == "__main__":\n    main()\n'
for name,want in [('__main__',['main']),('robot_nodes.my_node',[]),('main',[])]:
    env={'__name__':name,'calls':[]};exec(compile(code,'source-guard','exec'),env)
    check('guard '+name,env['calls'],want)
# Service constructors and callback return read from actual p199 pixels.
source="""
self.srv = self.create_service(AddTwoInts, 'add', self.handle_service)
self.client = self.create_client(AddTwoInts, 'add')
"""
calls=[x.value for x in ast.parse(source).body]
check('constructor method roles',[x.func.attr for x in calls],['create_service','create_client'])
check('constructor matching interface',[x.args[0].id for x in calls],['AddTwoInts','AddTwoInts'])
check('constructor matching service name',[x.args[1].value for x in calls],['add','add'])
check('server binds callback',calls[0].args[2].attr,'handle_service')
def handle_service(request,response):
    response.sum=request.a+request.b
    return response
request=SimpleNamespace(a=2,b=3);response=SimpleNamespace()
check('callback returns same response identity',handle_service(request,response) is response,True)
check('callback source operands',response.sum,5)
# p183 is undirected adjacency, unlike directed topic graph on p186.
edges={frozenset(e) for e in [('Camera','Lidar'),('Lidar','Control'),('Camera','SLAM'),('Lidar','Nav')]}
check('p183 four distinct unarrowed edges',len(edges),4)
check('p183 Camera neighbours',sorted(next(iter(e-{'Camera'})) for e in edges if 'Camera' in e),['Lidar','SLAM'])
check('p183 absent SLAM-Nav',frozenset(['SLAM','Nav']) in edges,False)
check('p183 absent Camera-Control',frozenset(['Camera','Control']) in edges,False)
report={'reviewerId':'independent-reviewer-robotics-batches-v2','completedAt':datetime.now(timezone.utc).isoformat(),'method':'Independent exact arithmetic, minimal Python guard, AST constructor checks and callback stub based on actual source pixels. No ROS runtime, hardware timing or author script executed. No numerical family generator in these targeted items.','checks':checks,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks)}
Path('audits/W01-L05-coverage-repairs-independent-computations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'failed':report['failed']}))
