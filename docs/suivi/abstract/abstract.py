import numpy as np
import os
import shutil

to_include = "to_include.txt"
abstract_file = "abstract.tex"
if os.path.exists(abstract_file):
    os.remove(abstract_file)

shutil.copyfile(to_include, abstract_file)
file_write = open(abstract_file,"a")
file_write.write('\n\\begin{document}\n')
file_write.write('\tLECOURTIER Frédérique \hfill \\today\n\t\\begin{center}\n\t\t\Large\\textbf{{Abstracts}}\n\t\end{center}\n')
repo = "../semaines/"

semaine_dir = np.array(os.listdir(repo))
num_dir = [x.split("_")[1] for x in semaine_dir]
mapping = np.argsort([int(x.split("-")[0]) for x in [x.split("_")[1] for x in os.listdir(repo)]])
semaine_dir = semaine_dir[mapping]

for i,dir_name in enumerate(semaine_dir):
    file_name = repo + dir_name + "/" + dir_name + ".tex"
    print(file_name)
    file_read = open(file_name, 'r')

    week_title = file_read.readline()
    file_write.write(week_title)

    word_to_search = "abstract"
    line = file_read.readline()

    while not (word_to_search in line):
        line = file_read.readline()
        if(len(line)==0):
            print("Pas d'abstract dans semaine_"+str(i))
            break
    
    if(len(line)!=0):
        line = file_read.readline()
        lines_to_write = []

        while not (word_to_search in line):
            lines_to_write.append(line)
            line = file_read.readline()
        
        for line_to_write in lines_to_write:
            file_write.write(line_to_write)

file_write.write('\end{document}')