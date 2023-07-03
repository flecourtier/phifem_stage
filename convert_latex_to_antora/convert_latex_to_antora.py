import numpy as np
import os
import sys
import shutil

"""
But : Convertir un fichier latex en une documentation antora complète
"""

root_dir = "/home/lecourtier/Bureau/rapport/"

source_dir = "rapport/"
rapport_file = root_dir + source_dir + "rapport.tex"
result_dir = root_dir + "antora/modules/ROOT/"
page_dir = result_dir + "pages/"

def search_word_in_line(word, line):
    # return true if word is in line
    return word in line

# list of all the sections and subsections
def list_sections():
    file_read = open(rapport_file, 'r')
    # we start by complete sections
    section_files = []
    empty_sections = []
    while line := file_read.readline():
        if search_word_in_line("\input", line):
            section_files.append(line.split("{")[1].split("}")[0])
        if search_word_in_line("\section", line):
            section_files.append("")
            empty_sections.append(line.split("{")[1].split("}")[0])
    section_files.pop(0)
    
    sections = {}
    for section in section_files:
        if section!="":
            file_read = open(root_dir + source_dir + section + ".tex", 'r')
            subsections = []
            while line := file_read.readline():
                if search_word_in_line("\section", line):
                    key = line.split("{")[1].split("}")[0]
                if search_word_in_line("\subsection", line):
                    subsections.append(line.split("{")[1].split("}")[0])
            sections[key] = subsections
        else:
            key = empty_sections.pop(0)
            sections[key] = None

    return section_files, sections

def create_nav_file(section_files,sections):
    # create the nav.adoc file
    nav_file = result_dir + "nav.adoc"
    file_write = open(nav_file, 'w')

    file_write.write("* xref:main_page.adoc[PhiFEM project]\n")

    for i,(section,subsections) in enumerate(sections.items()):        
        if section_files[i]!="":
            section_file_name = section_files[i].split("/")[1]
            file_write.write("** xref:" + section_file_name + ".adoc[" + section + "]\n")
            if subsections!=None:
                for j,subsection in enumerate(subsections):
                    file_write.write("*** xref:" + section_file_name + "/subsec_" + str(j) + ".adoc[" + subsection + "]\n")
        else:
            section_file_name = "section_" + str(i)
            file_write.write("** xref:" + section_file_name + ".adoc[" + section + "]\n")

    file_write.close()

def create_nav(section_files,sections):
    # remove all the files in the page directory
    if os.path.exists(page_dir):
        shutil.rmtree(page_dir)
    os.mkdir(page_dir)

    for i,(section,subsections) in enumerate(sections.items()):        
        if section_files[i]!="":
            section_file_name = section_files[i].split("/")[1]
            section_file = open(page_dir + section_file_name + ".adoc", 'w')
            section_file.write("= " + section + "\n")
            if subsections!=None:
                os.mkdir(page_dir + section_file_name)
                for j,subsection in enumerate(subsections):
                    subsection_file = open(page_dir + section_file_name + "/subsec_" + str(j) + ".adoc", 'w')
                    subsection_file.write("= " + subsection + "\n")
                    subsection_file.close()
            section_file.close()
        else:
            section_file_name = "section_" + str(i)
            section_file = open(page_dir + section_file_name + ".adoc", 'w')
            section_file.write("= " + section + "\n")
            section_file.close()            

section_files,sections = list_sections()
create_nav_file(section_files,sections)
create_nav(section_files,sections)
main_page_file = page_dir + "main_page.adoc"
file_write = open(main_page_file, 'w')
file_write.write("= PhiFEM project\n")
file_write.close()