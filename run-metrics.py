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

MT_SLOC = "SLOC"
MT_SLOCN = "SLOCbyname"
MT_SLOCNT = "SLOCbynametype"

PACKS = [
    ['../ioncore-python','ion', ['ION'], [M_PY_LOC]],
    ['../ioncore-python','ion/agents', ['IPA'], [M_PY_LOC]],
    ['../ioncore-python','ion/core', ['COI','COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/core/data', ['DM','DM-pres','-COI','-COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/core/object', ['DM','DM-mod','-COI','-COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/core/security', ['COI-idm','-COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/demo', ['ITV','ITV-ais'], [M_PY_LOC]],
    ['../ioncore-python','ion/integration/ais', ['ITV','ITV-ais'], [M_PY_LOC]],
    ['../ioncore-python','ion/integration/eoi', ['EOI'], [M_PY_LOC]],
    ['../ioncore-python','ion/interact', ['COI','COI-gov'], [M_PY_LOC]],
    ['../ioncore-python','ion/play', ['COI','COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/services/coi', ['COI','COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/services/coi/identity*', ['COI-idm','-COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/services/coi/resource*', ['COI-res','-COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/services/dm', ['DM','DM-dd'], [M_PY_LOC]],
    ['../ioncore-python','ion/services/dm/ingestion', ['DM-cat','-DM-dd'], [M_PY_LOC]],
    ['../ioncore-python','ion/services/dm/inventory', ['DM-cat','-DM-dd'], [M_PY_LOC]],
    ['../ioncore-python','ion/services/dm/presentation', ['DM-cat','-DM-dd'], [M_PY_LOC]],
    ['../ioncore-python','ion/services/dm/preservation', ['DM-pres','-DM-dd'], [M_PY_LOC]],
    ['../ioncore-python','ion/services/sa', ['SA','SA-man'], [M_PY_LOC]],
    ['../ioncore-python','ion/test', ['COI','COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/util', ['COI','COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','ion/zapps', ['COI','COI-cc'], [M_PY_LOC]],
    ['../ioncore-python','res', ['ION','ITV'], [M_CONF_LOC]],
    ['../ioncore-python','res/amqp', ['-ION','-ITV'], [M_CONF_LOC]],
    ['../ioncore-python','twisted', ['COI','COI-cc'], [M_PY_LOC]],

    ['../ioncore-java','src', ['ION','COI','COI-cc'], [M_JA_LOC]],

    ['../ion-object-definitions','python', ['ION','DM','DM-mod'], [M_PY_LOC]],
    ['../ion-object-definitions','net/ooici/cdm', ['ION','DM','DM-mod'], [M_PROTO_LOC]],
    ['../ion-object-definitions','net/ooici/core', ['ION','DM','DM-mod'], [M_PROTO_LOC]],
    ['../ion-object-definitions','net/ooici/integration/ais', ['ION','ITV','ITV-ais'], [M_PROTO_LOC]],
    ['../ion-object-definitions','net/ooici/integration/eoi', ['ION','EOI'], [M_PROTO_LOC]],
    ['../ion-object-definitions','net/ooici/play', ['ION','DM','DM-mod'], [M_PROTO_LOC]],
    ['../ion-object-definitions','net/ooici/services/coi', ['ION','COI','COI-cc'], [M_PROTO_LOC]],
    ['../ion-object-definitions','net/ooici/services/dm', ['ION','DM','DM-dd'], [M_PROTO_LOC]],
    ['../ion-object-definitions','net/ooici/services/sa', ['ION','SA','SA-reg'], [M_PROTO_LOC]],
    ['../ion-object-definitions','net/ooici/test', ['ION','DM','DM-mod'], [M_PROTO_LOC]],

    ['../ion-integration','ionint', ['ION','ITV','ITV-test'], [M_PY_LOC]],
    ['../ion-integration','inttests', ['ION','ITV','ITV-test'], [M_PY_LOC]],
    ['../ion-integration','itv_trial', ['ION','ITV','ITV-code'], [M_PY_LOC]],
    ['../ion-integration','src', ['ION','ITV','ITV-test'], [M_JA_LOC]],
    ['../ion-integration','tests', ['ION','ITV','ITV-test'], [M_PY_LOC]],

    ['../ooici-pres','.', ['ION','COI','COI-cc'], [M_JA_LOC, M_GROOVY_LOC]],
    ['../ooici-pres','src/java', ['-COI-cc','COI-idm'], [M_JA_LOC, M_GROOVY_LOC]],
    ['../ooici-pres','.', ['ION','UI'], [M_WEB_LOC]],

    ['../epu','epu', ['ION','CEI','CEI-ela'], [M_PY_LOC]],

    ['../epuagent','epuagent', ['ION','CEI','CEI-ee'], [M_PY_LOC]],

    ['../eoi-agents','src', ['ION','EOI'], [M_JA_LOC]],

    ['../dt-data','.', ['ION','CEI','CEI-ee','CEI-conf'], [M_RB_LOC, M_CONF_LOC]],

    ['../launch-plans','.', ['ION','CEI','CEI-ee','CEI-conf'], [M_RB_LOC, M_CONF_LOC]],

    ['../txrabbitmq','.', ['ION','CEI','CEI-ela'], [M_PY_LOC]],

    ['../cloudinit.d','.', ['ION','CEI','CEI-ee'], [M_PY_LOC, M_CONF_LOC]],

    ['../epumgmt','.', ['ION','CEI','CEI-ee'], [M_PY_LOC, M_CONF_LOC]],

    ['../Nimboss','.', ['ION','CEI','CEI-ee'], [M_PY_LOC, M_CONF_LOC]],

]

ALIASES = {
    'BuzzTroll':'John Bresnahan',
    'Timothy':'Timothy LaRocque',
    'timf':'Tim Freeman',
    'mmeisinger':'Michael Meisinger',
    'arjuna':'Arjuna Balasurya',
    'brianfox':'Brian Fox',
}

def add_to_metrics(metrics, package, mtype, counter, metric, count):

    print "Package:%s counter:%s metric:%s count=%s" % (package, counter, metric, count)

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
                add_to_metrics(metrics, p_pack, MT_SLOCN, counter, xname, count)
                add_to_metrics(metrics, p_pack, MT_SLOCNT, counter, "%s:%s" % (ext,xname), count)

        cmd = "rm namecount.tmp"
        res = os.popen(cmd).read()

def measure_package(metrics, pack):
    p_path, p_pack, p_counters, p_metricprocs = pack

    if M_PY_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.py' -prune | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_pack, MT_SLOC, counter, M_PY_LOC, count)
        count_by_name(metrics, pack, ['py'], M_PY_LOC)

    if M_JA_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.java' -prune | xargs cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_pack, MT_SLOC, counter, M_JA_LOC, count)
        count_by_name(metrics, pack, ['java'], M_PY_LOC)

    if M_GROOVY_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.groovy' -prune | xargs cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_pack, MT_SLOC, counter, M_GROOVY_LOC, count)
        count_by_name(metrics, pack, ['groovy'], M_PY_LOC)

    if M_RB_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.rb' -prune | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.erb' -prune | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_pack, MT_SLOC, counter, M_RB_LOC, count)
        count_by_name(metrics, pack, ['rb','erb'], M_PY_LOC)

    if M_CONF_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.conf' -prune | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.app' -prune | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.rel' -prune | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.properties' -prune | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.xml' -prune | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.sh' -prune | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.json' -prune | xargs cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_pack, MT_SLOC, counter, M_CONF_LOC, count)
        count_by_name(metrics, pack, ['conf','app','rel','properties','xml','sh','json'], M_PY_LOC)

    if M_PROTO_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.proto' -prune | xargs cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_pack, MT_SLOC, counter, M_PROTO_LOC, count)
        count_by_name(metrics, pack, ['proto'], M_PY_LOC)

    if M_WEB_LOC in p_metricprocs:
        cmd = "find %s/%s -name '*.gsp' -prune | xargs cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count = int(os.popen(cmd).read())
        cmd = "find %s/%s -name '*.html' -prune | xargs cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        count += int(os.popen(cmd).read())
        #cmd = "find %s/%s -name '*.js' -prune | xargs cat | sed '/^\s*\/\//d;/^\s*$/d' | wc -l" % (p_path, p_pack)
        #count += int(os.popen(cmd).read())
        for counter in p_counters:
            add_to_metrics(metrics, p_pack, MT_SLOC, counter, M_WEB_LOC, count)
        count_by_name(metrics, pack, ['gsp','html'], M_PY_LOC)


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

    print "Metrics results:"
    pprint.pprint(metrics)

    write_csv(metrics, datestr)

if __name__ == "__main__":
    main_collect(PACKS)
