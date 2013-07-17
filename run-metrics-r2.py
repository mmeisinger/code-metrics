#!/usr/bin/env python

"""
@file run-metrics.py
@author Michael Meisinger
@brief Collect some code metrics
"""

import os, subprocess, sys, string, pprint, re

GIT_PULL = False
BY_NAME = True

RESULTS_DIR = "results"

M_PY_LOC = 'SLOCpy'
M_JA_LOC = 'SLOCja'
M_GROOVY_LOC = 'SLOCgroovy'
M_RB_LOC = 'SLOCrb'
M_CONF_LOC = 'SLOCconf'
M_PROTO_LOC = 'SLOCproto'
M_WEB_LOC = 'SLOCweb'
M_JS_LOC = 'SLOCjs'
M_C_LOC = 'SLOCc'

MT_SLOC = "SLOC"
MT_SLOCN = "SLOCbyname"
MT_SLOCNT = "SLOCbynametype"

PACKS = [
    ['../pyon','pyon', ['ION', 'pyon', 'COI'], [M_PY_LOC]],
    ['../pyon','examples', ['ION', 'pyon', 'INT'], [M_PY_LOC]],
    ['../pyon','prototype', ['ION', 'pyon', 'INT'], [M_PY_LOC]],
    ['../pyon','putil', ['ION', 'pyon', 'INT'], [M_PY_LOC]],
    ['../pyon','scripts', ['ION', 'pyon', 'INT'], [M_PY_LOC]],

    ['../coi-services','ion', ['ION', 'services'], [M_PY_LOC]],
    ['../coi-services','ion/agents', ['SA'], [M_PY_LOC]],
    ['../coi-services','ion/agents/cei', ['-SA', 'CEI'], [M_PY_LOC]],
    ['../coi-services','ion/agents/data', ['-SA', 'EOI'], [M_PY_LOC]],
    ['../coi-services','ion/core', ['COI'], [M_PY_LOC]],
    ['../coi-services','ion/processes', ['DM'], [M_PY_LOC]],
    ['../coi-services','ion/processes/bootstrap', ['-DM', 'COI'], [M_PY_LOC]],
    ['../coi-services','ion/processes/data/transforms/viz', ['-DM', 'AS'], [M_PY_LOC]],
    ['../coi-services','ion/services/ANS', ['AS'], [M_PY_LOC]],
    ['../coi-services','ion/services/coi', ['COI'], [M_PY_LOC]],
    ['../coi-services','ion/services/dm', ['DM'], [M_PY_LOC]],
    ['../coi-services','ion/services/sa', ['SA'], [M_PY_LOC]],
    ['../coi-services','ion/services/cei', ['CEI'], [M_PY_LOC]],
    ['../coi-services','ion/services/eoi', ['EOI'], [M_PY_LOC]],
    ['../coi-services','ion/simulators', ['MI'], [M_PY_LOC]],
    ['../coi-services','ion/util', ['COI'], [M_PY_LOC]],

    ['../coi-services','extern/ion-definitions/objects', ['ION', 'ARCH'], [M_CONF_LOC]],

    ['../ion-ux','main.py', ['ION','UX'], [M_PY_LOC]],
    ['../ion-ux','service_api.py', ['ION','UX'], [M_PY_LOC]],
    ['../ion-ux','layout_api.py', ['ION','UX'], [M_PY_LOC]],
    ['../ion-ux','templates', ['ION','UX'], [M_WEB_LOC, M_JS_LOC]],
    ['../ion-ux','static/js/ux-*', ['ION','UX'], [M_JS_LOC]],
    ['../ion-ux','static/js/ion-*', ['ION','UX'], [M_JS_LOC]],
    ['../ion-ux','static/js/IONUX*', ['ION','UX'], [M_JS_LOC]],

    ['../coverage-model','coverage_model', ['ION', 'DM'], [M_PY_LOC]],

    ['../marine-integrations','mi', ['ION', 'MI'], [M_PY_LOC]],

    ['../port_agent','tools', ['ION', 'MI'], [M_PY_LOC]],
    ['../port_agent','src', ['ION', 'MI'], [M_C_LOC]],

    ['../utilities','src', ['ION', 'INT'], [M_PY_LOC]],
    ['../utilities','test', ['ION', 'INT'], [M_PY_LOC]],

    ['../ape','.', ['ION', 'INT'], [M_PY_LOC]],

    ['../epu','epu', ['ION','CEI'], [M_PY_LOC]],

    ['../dt-data','.', ['ION','INT'], [M_RB_LOC, M_CONF_LOC]],

    ['../launch-plans','.', ['ION','INT'], [M_RB_LOC, M_CONF_LOC]],

    ['../cloudinit.d','.', ['ION','CEI'], [M_PY_LOC, M_CONF_LOC]],

    ['../pidantic','pidantic', ['ION','CEI'], [M_PY_LOC]],

    ['../ceiclient','ceiclient', ['ION','CEI'], [M_PY_LOC]],

    ['../eeagent','.', ['ION','CEI'], [M_PY_LOC]],

    ['../epuharness','.', ['ION','CEI'], [M_PY_LOC, M_CONF_LOC]],

    ['../epumgmt','src', ['ION','CEI'], [M_PY_LOC, M_CONF_LOC]],
]

ALIASES = {
    'BuzzTroll':'John Bresnahan',
    'Timothy':'Timothy LaRocque',
    'timf':'Tim Freeman',
    'mmeisinger':'Michael Meisinger',
    'arjuna':'Arjuna Balasurya',
    'brianfox':'Brian Fox',
    'oldpatricka':'Patrick Armstrong',
    'unwin':'Roger Unwin',
    'ijk5':'Ian Katz',
    'seman':'Seman Said',
    'rumi':'Rumi Neykova',
    'Rumyana Neykova':'Rumi Neykova',
    'wfrench':'Bill French',
    'Jeff Laughlin Consulting LLC':'Jeff Laughlin',
    'jlaughlin':'Jeff Laughlin',

}

def add_to_metrics(metrics, package, sdir, mtype, counter, metric, count):
    if package.startswith("../"):
        package = package[3:]

    if counter.startswith("-"):
        print "  %s: %s %s[%s] MINUS %s" % (package, sdir, counter[1:], metric, count)
    else:
        print "  %s: %s %s[%s] PLUS %s" % (package, sdir, counter, metric, count)

    if not mtype in metrics:
        metrics[mtype] = {}
    tdict = metrics[mtype]

    if counter.startswith("-"):
        counter = counter[1:]

        if not counter in tdict:
            tdict[counter] = {}
        cdict = tdict[counter]

        mcount = cdict.get(metric, 0)
        mcount -= int(count)
        cdict[metric] = mcount

        scount = cdict.get("TOTAL", 0)
        scount -= int(count)
        cdict["TOTAL"] = scount
    else:
        if not counter in tdict:
            tdict[counter] = {}
        cdict = tdict[counter]

        mcount = cdict.get(metric, 0)
        mcount += int(count)
        cdict[metric] = mcount

        scount = cdict.get("TOTAL", 0)
        scount += int(count)
        cdict["TOTAL"] = scount

def count_by_name(metrics, pack, extensions, metric):
    if not BY_NAME:
        return

    p_path, p_pack, p_counters, p_metricprocs = pack

    curpath = os.getcwd()

    for ext in extensions:
        cmd = "(cd %s; find %s -name '*.%s' -prune | xargs -L 1 git blame > %s/namecount.tmp)" % (p_path, p_pack, ext, curpath)
        res = os.popen(cmd).read()

        rex = r'^[^\(]+\((.+?)\s+20\d\d-\d\d-\d\d\s[^\(]+\)\s*(\S*)\s*$'
        all_names = []
        blamefile = open("namecount.tmp","r")
        line = blamefile.readline()
        empty = 0
        while line:
            line = blamefile.readline()
            lnamem = re.search(rex, line)
            if not lnamem:
                continue
            lname = lnamem.group(1)
            lcont = lnamem.group(2)
            if not lname in all_names:
                all_names.append(lname)
            if lcont == '' or lcont.startswith('#') or lcont.startswith('//'):
                empty += 1

        blamefile.close()

        #print "Names in file", all_names
        #print "Empty lines", empty

        for name in all_names:
            cmd = "cat namecount.tmp | grep '%s' | wc -l" % (name)
            count = int(os.popen(cmd).read())

            xname = ALIASES.get(name, name)

            for counter in p_counters:
                add_to_metrics(metrics, p_path, p_pack, MT_SLOCN, counter, xname, count)
                add_to_metrics(metrics, p_path, p_pack, MT_SLOCNT, counter, "%s:%s" % (ext,xname), count)

        cmd = "rm namecount.tmp"
        res = os.popen(cmd).read()

def measure_package(metrics, pack):
    p_path, p_pack, p_counters, p_metricprocs = pack

    if M_PY_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.py' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_path, p_pack, MT_SLOC, counter, M_PY_LOC, count)
        count_by_name(metrics, pack, ['py'], M_PY_LOC)

    if M_JA_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.java' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_path, p_pack, MT_SLOC, counter, M_JA_LOC, count)
        count_by_name(metrics, pack, ['java'], M_PY_LOC)

    if M_C_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.cxx' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*\/\*/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.h' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*\/\*/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_path, p_pack, MT_SLOC, counter, M_C_LOC, count)
        count_by_name(metrics, pack, ['cxx','h'], M_C_LOC)

    if M_GROOVY_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.groovy' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_path, p_pack, MT_SLOC, counter, M_GROOVY_LOC, count)
        count_by_name(metrics, pack, ['groovy'], M_PY_LOC)

    if M_RB_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.rb' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.erb' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_path, p_pack, MT_SLOC, counter, M_RB_LOC, count)
        count_by_name(metrics, pack, ['rb','erb'], M_PY_LOC)

    if M_CONF_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.conf' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.app' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.rel' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.properties' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.xml' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.sh' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.json' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.yml' -prune -print0 | xargs -0 cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_path, p_pack, MT_SLOC, counter, M_CONF_LOC, count)
        count_by_name(metrics, pack, ['conf','app','rel','properties','xml','sh','json','yml'], M_PY_LOC)

    if M_PROTO_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.proto' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_path, p_pack, MT_SLOC, counter, M_PROTO_LOC, count)
        count_by_name(metrics, pack, ['proto'], M_PY_LOC)

    if M_WEB_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.gsp' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.html' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        #cmd = "find %s/%s -name '*.js' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        #count += int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_path, p_pack, MT_SLOC, counter, M_WEB_LOC, count)
        count_by_name(metrics, pack, ['gsp','html'], M_PY_LOC)

    if M_JS_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.js' -prune -print0 | xargs -0 cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_path, p_pack, MT_SLOC, counter, M_JS_LOC, count)
        count_by_name(metrics, pack, ['js'], M_PY_LOC)

def write_csv(metrics, unique):
    outfile = open('results/code-metrics_%s.csv' % unique,'w')

    outfile.write("Type,Counter,Metric,Value\n")
    for typs in metrics.iteritems():
        tname, tdict = typs
        for ctrs in tdict.iteritems():
            cname, cdict = ctrs
            for counter in cdict.iteritems():
                mname, value = counter
                line = "%s,%s,%s,%s\n" % (tname, cname, mname, value)
                outfile.write(line)

    outfile.close()

def main_collect(packages):
    print "Collecting code metrics"
    datestr = os.popen("date +%Y-%m-%d_%H-%M-%S").read()
    resdir = "%s/metrics_%s" % (RESULTS_DIR, datestr)
    print resdir

    metrics = {}

    paths = []
    for entry in packages:
        p_dir = entry[0]
        if p_dir not in paths:
            paths.append(p_dir)

    if GIT_PULL:
        for p_dir in paths:
            cmd = "(cd %s; git pull)" % (p_dir)
            res = os.popen(cmd).read()
            print "PULL ", p_dir, res

    for entry in packages:
        measure_package(metrics, entry)

    print "Scanned packages:"
    for p in sorted(paths):
        if p.startswith("../"):
            p = p[3:]
            print " ", p

    print "Metrics results:"
    pprint.pprint(metrics)

    write_csv(metrics, datestr)

if __name__ == "__main__":
    main_collect(PACKS)
