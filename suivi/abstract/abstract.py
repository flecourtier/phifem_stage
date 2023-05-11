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
repo = "../semaines/semaine_"

i=1
repo_name = repo+str(i)

while( os.path.exists(repo_name) ):
    file_name = repo_name + "/semaine_" + str(i) + ".tex"
    file_read = open(file_name, 'r')

    week_title = file_read.readline()
    file_write.write(week_title)

    word_to_search = "abstract"
    line = file_read.readline()

    while not (word_to_search in line):
        line = file_read.readline()

    line = file_read.readline()
    lines_to_write = []

    while not (word_to_search in line):
        lines_to_write.append(line)
        line = file_read.readline()
    
    for line_to_write in lines_to_write:
        file_write.write(line_to_write)

    i+=1
    repo_name = repo+str(i)

file_write.write('\end{document}')