#!/usr/bin/env python
import os
import shutil
import sys

# This script should be executed from the root directory of Doop.

# ----------------- configuration -------------------------
DOOP = './run --color '
PRE_ANALYSIS = 'context-insensitive'
MAIN_ANALYSIS = 'scaler-sensitive+heap'
DATABASE = 'last-analysis'

APP = 'temp'

SCALER_HOME = '../scaler'
SCALER_CP = ':'.join([
    os.path.join(SCALER_HOME, 'build', 'scaler.jar'),
    os.path.join(SCALER_HOME, 'lib', 'guava-23.0.jar'),
])
SCALER_MAIN = 'ptatoolkit.scaler.Main'
SCALER_PTA = 'ptatoolkit.scaler.doop.DoopPointsToAnalysis'
SCALER_CACHE = 'cache/scaler'
SCALER_OUT = 'results'
SCALER_DEF_TST = 30000000
SCALER_MEMORY = '48g'

# ---------------------------------------------------------

RESET = '\033[0m'
YELLOW = '\033[33m'
BOLD = '\033[1m'

def runPreAnalysis(argDict):
    args = [DOOP] + argDict['args'] + [PRE_ANALYSIS] + argDict['jars']
    cmd = ' '.join(args)
    print YELLOW + BOLD + 'Running pre-analysis ...' + RESET
    # print cmd
    os.system(cmd)

QUERY={
    # points-to set
    'VPT':"Stats:Simple:InsensVarPointsTo",

    # object
    'OBJ':"_(obj)<-Stats:Simple:InsensVarPointsTo(obj,_).",
    'OBJ_TYPE':"_[obj]=type<-" +
                "HeapAllocation:Type[obj]=type," +
                "Stats:Simple:InsensVarPointsTo(obj,_).",
    'SPECIAL_OBJECTS':"HeapAllocation:Special",
    'MERGE_OBJECTS':"HeapAllocation:Merge",
    'STRING_CONSTANTS':"StringConstant",
    'REF_STRING_CONSTANTS':"ReflectionStringConstant",
    
    'OBJECT_IN':"_(obj,inmethod)<-" +
            "AssignHeapAllocation(obj,_,inmethod)," +
            "Reachable(inmethod).",
    'OBJECT_ASSIGN':"_(obj,var)<-" +
            "AssignHeapAllocation(obj,var,inmethod)," +
            "Reachable(inmethod).",
    'REF_OBJECT':"_(obj,callsite)<-" +
                "ReflectiveHeapAllocation[callsite,_]=obj.",

    'STRING_CONSTANT':"<<string-constant>>",

    # call graph edges
    'REGULARCALL':"Stats:Simple:InsensCallGraphEdge",
    'REFCALL':"_(from,to)<-ReflectiveCallGraphEdge(_,from,_,to).",
    'NATIVECALL':"_(from,to)<-NativeCallGraphEdge(_,from,_,to).",
    'CALL_EDGE':"Stats:Simple:WholeInsensCallGraphEdge",
    'CALLER_CALLEE':"_(caller,callee)<-" +
            "(Stats:Simple:InsensCallGraphEdge(callsite,callee);" +
            "ReflectiveCallGraphEdge(_,callsite,_,callee))," +
            "(SpecialMethodInvocation:In(callsite,caller);" +
            "VirtualMethodInvocation:In(callsite,caller);" +
            "StaticMethodInvocation:In(callsite,caller)).",
    'MAINMETHOD':"MainMethodDeclaration",
    'REACHABLE':"Reachable",
    'IMPLICITREACHABLE':"ImplicitReachable",

    # call site
    'INST_CALL':"_(callsite,callee)<-" +
            "Stats:Simple:InsensCallGraphEdge(callsite,callee)," +
            "(VirtualMethodInvocation(callsite,_,_);" +
            "SpecialMethodInvocation:Base[callsite]=_).",
    'INST_CALL_RECV':"_(callsite,recv)<-" +
            "Stats:Simple:InsensCallGraphEdge(callsite,_)," +
            "(VirtualMethodInvocation:Base[callsite]=recv;" +
            "SpecialMethodInvocation:Base[callsite]=recv).",
    'INST_CALL_ARGS':"_(callsite,arg)<-" +
            "Stats:Simple:InsensCallGraphEdge(callsite,_)," +
            "(VirtualMethodInvocation(callsite,_,_);" +
            "SpecialMethodInvocation:Base[callsite]=_)," +
            "ActualParam[_,callsite]=arg.",
    'CALLSITEIN':"MethodInvocation:In",

    # method
    'THIS_VAR':"_(mtd,this)<-Reachable(mtd),ThisVar[mtd]=this.",
    'PARAMS':"_(mtd,param)<-Reachable(mtd),FormalParam[_,mtd]=param.",
    'RET_VARS':"_(mtd,ret)<-Reachable(mtd),ReturnVar(ret,mtd).",
    # only instance methods have this variables
    'INST_METHODS':"_(mtd)<-Reachable(mtd),ThisVar[mtd]=_.",
    'OBJFINAL':"ObjectSupportsFinalize",
    'VAR_IN':"_(var,inmethod)<-Var:DeclaringMethod(var,inmethod)," +
                   "Reachable(inmethod).",
    'METHOD_MODIFIER':"_(mtd,mod)<-MethodModifier(mod,mtd).",

    # type
    'APPLICATION_CLASS':"ApplicationClass",
    'DIRECT_SUPER_TYPE':"DirectSuperclass",
    'DECLARING_CLASS_ALLOCATION':"DeclaringClassAllocation",
}

def dumpDoopResults(db_dir, dump_dir, app, query):
    output = os.path.join(dump_dir, '%s.%s' % (app, query))
    if os.path.exists(output):
        os.remove(output) # remove old file
    cmd = "bloxbatch -db %s -query '%s' > %s" % (db_dir, QUERY[query], output)
    # print cmd
    os.system(cmd)

def dumpRequiredDoopResults(app, db_dir, dump_dir):
    print 'Dumping doop analysis results ...'
    REQUIRED_QURIES = [
        'CALL_EDGE', 'CALLSITEIN',
        'DECLARING_CLASS_ALLOCATION', 'INST_METHODS',
        'OBJECT_IN', 'SPECIAL_OBJECTS',
        'THIS_VAR',  'VAR_IN', 'VPT',
    ]
    if not os.path.isdir(dump_dir):
        os.makedirs(dump_dir)
    for query in REQUIRED_QURIES:
        dumpDoopResults(db_dir, dump_dir, app, query)
    
def runScaler(app, cache_dir, out_dir, tst):
    scaler_file = os.path.join(out_dir, \
        '%s-ScalerMethodContext-TST%d.facts' % (app, tst))
    if os.path.exists(scaler_file):
        os.remove(scaler_file) # remove old file
    cmd = 'java -Xmx%s ' % SCALER_MEMORY
    cmd += ' -cp %s ' % SCALER_CP
    cmd += SCALER_MAIN
    cmd += ' -pta %s ' % SCALER_PTA
    cmd += ' -app %s ' % app
    cmd += ' -cache %s ' % cache_dir
    cmd += ' -out %s ' % out_dir
    cmd += ' -tst %d ' % tst
    # print cmd
    os.system(cmd)
    return scaler_file

def runMainAnalysis(argDict, scaler_file):
    args = [DOOP, '--cache', '-scaler', scaler_file] +\
        argDict['args'] + [MAIN_ANALYSIS] + argDict['jars']
    cmd = ' '.join(args)
    print YELLOW + BOLD + 'Running main (Scaler-guided) analysis ...' + RESET
    # print cmd
    os.system(cmd)

def run(args):
    argDict = parseArgs(args)
    runPreAnalysis(argDict)
    dumpRequiredDoopResults(APP, DATABASE, SCALER_CACHE)
    scaler_file = runScaler(APP, SCALER_CACHE, SCALER_OUT, argDict['tst'])
    runMainAnalysis(argDict, scaler_file)

def parseArgs(args):
    results = { 'args': [], 'jars': [], 'tst': SCALER_DEF_TST }
    i = 0
    inArgs = True
    while i < len(args):
        if args[i] == '-tst':
            temp = args[i + 1]
            if temp[-1] in ['M', 'm']:
                tst = int(temp[:-1]) * 1000000
            else:
                tst = int(temp)
            results['tst'] = tst
            i += 2
            continue
        if args[i].endswith('.jar'):
            results['jars'].append(args[i])
            inArgs = False
        if inArgs:
            results['args'].append(args[i])
        i += 1
    return results

if __name__ == '__main__':
    run(sys.argv[1:])
