def gatherAnnotations(scriptPath):
    annotations = []
    with open(scriptPath) as file:
        script = file.readlines()
        for index, line in enumerate(script):
            if '# @prov' in line or '#@prov' in line:
                annotation = line
                i = 1
                if (index + i) < len(script):
                    if '#' in script[index + i] and '@prov' not in script[index + i]:
                        annotation += (script[index + i])
                        i += i
                annotations.append(annotation
                    .replace('#','')
                    .replace('\n','')
                    .replace('  ','')
                    .strip()
                    )
    return annotations

def parseInit(init):
    ns = "Namespace(\"https://customNamespace.com/" + init + "/\")"
    return ns

def parseUnit(unit):
    data = []

    outputs = unit.split('=')[0].replace(' ','').split(',')
    process = unit.split('=')[1].split('(')[0].replace(' ','')
    inputs = unit.split('=')[1].split('(')[1].split(')')[0].replace(' ','').split(',')
    procType = unit.split('=')[1].split('(')[1].split(')')[1].replace(' ','')
    if not procType:
        procType = 'noType'

    for inpt in inputs:
        cmd = "addData(CNS." + inpt + ")"
        data.append(cmd)

    for output in outputs:
        cmd = "addData(CNS." + output + ")"
        data.append(cmd)

    process = "addProcess(CNS." + process + ",GEOKUR." + procType + ")"
    
    link = ["link(\
        inputs = " + str(["CNS." + s for s in inputs]).replace("'", '') + ",\
        process = CNS.", ",\
        outputs = " + str(["CNS." + s for s in outputs]).replace("'", '') +\
        ")"]
    
    return data, process, link


