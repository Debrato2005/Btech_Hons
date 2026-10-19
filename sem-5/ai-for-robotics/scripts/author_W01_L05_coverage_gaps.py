from authoring_helpers import DraftBatch
b=DraftBatch('W01-L05-COVERAGE-GAP',1,'L05','Robot Operating System',171,'robotics-integration-L05-coverage-gap-author')
b.add(183,'unarrowed-adjacency','Read the five-node connectivity drawing','Which set matches all four direct connections in the five-node drawing?',[
 'Camera–Lidar; Lidar–Control; Camera–SLAM; Lidar–Nav',
 'Camera–Lidar; Lidar–Control; Camera–Nav; Lidar–SLAM',
 'Camera–Control; Lidar–Control; Camera–SLAM; Lidar–Nav',
 'Camera–Lidar; Lidar–Control; SLAM–Nav; Camera–Control'],0,
 'The visible lines connect Camera to Lidar and SLAM, and Lidar to Control and Nav; there are no arrowheads or topic labels.',[
 'This matches the four visible line segments.',
 'This swaps the lower branches: Camera connects to SLAM, and Lidar connects to Nav.',
 'The upper-left segment joins Camera to Lidar, not directly to Control.',
 'Neither SLAM–Nav nor Camera–Control is drawn as a direct connection.'],typ='diagram',difficulty='easy',assumptions=['Read connectivity only; the figure gives no publication direction, topic name or message type.'])
b.add(190,'message-transfer-overhead','Explain the high-bandwidth message motivation','Why does the slide discuss optimized message structures for high-bandwidth video moving between AI nodes and hardware drivers?',[
 'To reduce the computational and data-transfer overhead of moving the data',
 'To reduce the number of mechanical joints in the robot model',
 'To make raw camera pixels use the velocity-command interface instead',
 'To replace camera acquisition with the navigation node’s target pose'],0,
 'The source’s quoted data-movement “cost” concerns handling high-bandwidth data between software/hardware components, not changing what the camera or robot model represents.',[
 'This is the stated data-movement motivation, without asserting zero-copy or unlimited throughput.',
 'Message transfer does not change the mechanism’s number of joints.',
 'Optimizing transport does not make image pixels and velocity commands the same interface.',
 'A desired pose is not a substitute for the sensor data being transferred.'],typ='conceptual',difficulty='easy',assumptions=['Assess the source’s motivation, not an exact bandwidth measurement or a guarantee that every deployment uses zero-copy transfer.'])
b.add(199,'service-endpoint-construction','Match the server and client interface in the code','Which interpretation of the shown server/client construction and handler return is correct?',[
 'create_service uses AddTwoInts and add with handle_service; create_client uses AddTwoInts and add; the handler returns response',
 'create_service uses AddTwoInts and add with handle_service; create_client uses String and add; the handler returns response',
 'create_service uses AddTwoInts and add with handle_service; create_client uses AddTwoInts and speed; the handler returns response',
 'create_service uses AddTwoInts and add with handle_service; create_client uses AddTwoInts and add; the handler returns request'],0,
 'Both endpoints use the same AddTwoInts service interface and add name; the server binds handle_service, which fills and returns the response object.',[
 'This matches both endpoint constructors and the final return line.',
 'The displayed client uses AddTwoInts, not String.',
 'The displayed client uses add; speed is the separately declared parameter name.',
 'The handler returns response after setting response.sum, not the request.'],typ='code_output',difficulty='easy',assumptions=['This concerns the printed constructors and handler, not whether an executor has completed or consumed the asynchronous result.'])
for c in b.questions[-1]['citations']:c['kind']='code'
b.save()
print('3 distinct source-gap drafts frozen.')
