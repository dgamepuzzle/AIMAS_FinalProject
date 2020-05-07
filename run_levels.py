import os
import subprocess

directory = os.fsencode('C:\\Users\\carlo\\workspace\\artificial_intelligence\\AIMAS_FinalProject\\OldTrainingLevels\\comp17\\')
strategies = ['bfs', 'dfs', 'greedy', 'astar', 'wastar']

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith('.lvl'):
        level = '{}{}'.format(os.fsdecode(directory), filename)
        # print(level)
        for strategy in strategies:
            out = subprocess.Popen(['java', '-jar', 'server.jar', '-l', level, '-c',
                                    'python NewSearchClient/mainsearchclient.py --max-memory 2048 -'+strategy+' --csv C:\\Users\\carlo\\workspace\\artificial_intelligence\\AIMAS_FinalProject\\test.csv',
                                    '-g', '150', '-t', '300'], 
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print(subprocess.list2cmdline(out.args))
            stdout, stderr = out.communicate()
            # print(stdout.decode('utf-8'))
            # print(stderr.decode('utf-8'))

