#!/usr/bin/python


import re
import os.path


GWT = re.compile('^\s+(Given|When|Then) (.+)\s+$')


def parse(file):
    feature = {'title': None,
               'description': None,
               'scenarios': [],
               'file': file.name}
    cursor = None
    is_comment = False
    current_scenario = {'title': None,
                        'steps': []}
    for _line in file.readlines():
        if _line.startswith('Feature'):
            cursor = 'Feature'
            feature['title'] = _line.strip()[len('Feature: '):]
            continue
        elif _line.strip().startswith('Scenario: '):
            cursor = 'Scenario'
            current_scenario['title'] = _line.strip()[len('Scenario: '):]
            continue
        elif GWT.match(_line):
            clause, content = GWT.match(_line).groups()
            step = {'clause': clause,
                    'content': content}
            current_scenario['steps'].append(step)
            continue
        else:
            if _line.strip() in ['', '\n'] and is_comment is False:
                if cursor == 'Scenario':
                    # archive scenario
                    feature['scenarios'].append(current_scenario)
                    current_scenario = {'title': None,
                                        'steps': []}
                # reset cursor
                cursor = None
            else:
                line = _line.strip()
                if len(line) < 1:
                    line = '\n'
                if cursor == 'Feature':
                    feature['description'] = line
                elif cursor == 'Scenario':
                    if '"""' in _line:
                        if is_comment:
                            # end of comment
                            is_comment = False
                        else:
                            is_comment = True
                            line = '\n' + line
                    current_scenario['steps'][-1]['content'] += line
                    if is_comment:
                        current_scenario['steps'][-1]['content'] += '\n'
    # close any unfinished business
    if cursor == 'Scenario':
        feature['scenarios'].append(current_scenario)
    return feature


def dict2adoc(feature, name=None):
    if not name:
        name = feature['title']
    adoc = """%s(7)
%s
:doctype: manpage


NAME
----
%s - autogenerated from feature spec `%s`


SYNOPSIS
--------

%s


""" % (feature['title'],
       '=' * len(feature['title']) + '===',
       name,
       os.path.basename(feature['file']),
       feature.get('description', '.'))
    adoc += "SCENARIOS\n---------\n\n"
    for scenario in feature.get('scenarios', []):
        adoc += "%s\n%s\n\n" % (scenario['title'],
                                '~' * len(scenario['title']))
        for step in scenario.get('steps', []):
            if '\n' in step['content']:
                fl, rest = step['content'].split('\n', 1)
            else:
                fl, rest = step['content'], None
            adoc += "* *_%s_* %s" % (step['clause'], fl)
            if rest:
                adoc += "\n....\n%s\n....\n" % rest
            else:
                adoc += ",\n"
        if adoc.endswith('....\n'):
            adoc += '\n'
        else:
            adoc = adoc[:-2] + '\n\n'
    return adoc


if __name__ == '__main__':
    import sys
    import glob

    path = sys.argv[1]
    for f in glob.glob(path):
        # foo.feature -> rdopkg.feature-foo.7.adoc
        basefn = re.sub(r'(.+)\.feature$',
                        'rdopkg-feature-\g<1>',
                        f.split('/')[-1])
        output = basefn + '.7.adoc'
        with open(f) as feature, open(output, 'w') as adoc:
            adoc.write(dict2adoc(parse(feature), name=basefn))
