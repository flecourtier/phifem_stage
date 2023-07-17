import numpy as np
import os
import shutil

"""
But : Convertir un fichier latex en une documentation antora complète
"""

root_dir = "../../docs/"

source_dir = "rapport/"
rapport_file = root_dir + source_dir + "rapport.tex"
result_dir = root_dir + "antora/modules/ROOT/"
page_dir = result_dir + "pages/"
images_dir = result_dir + "assets/images/"

# return true if word is in line
def search_word_in_line(word, line):
    return word in line

# test if the title contains a latex formula
def test_latex_title(title):
    if search_word_in_line("$", title):
        title_split = title.split("$")
        title = ""
        start_stem = 0
        for i,part in enumerate(title_split):
            title += part
            if start_stem==0 and i!=len(title_split)-1:
                title += "stem:["
                start_stem = 1
            elif start_stem==1 and i!=len(title_split)-1:
                title += "]"
                start_stem = 0

    return title

# read "rapport.tex" and return the list of the files of the sections (e.g. "sections/section_1")
# for section which are no input, we juste create an empty section
def get_section_files():
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

    return section_files,empty_sections

# return the list of the sections and the list of the subsections
# if there is paragraph, we creates file for subsubsection 
# {"section1":[subsection1,subsection2],"section2":[subsection1,subsection2]}
def get_sections(section_files,empty_sections):
    def test_paragraph(section):
        file_read = open(root_dir + source_dir + section + ".tex", 'r')
        while line := file_read.readline():
            if search_word_in_line("\paragraph", line):
                return True
        return False

    sections = {}
    for section in section_files:
        if section!="":
            file_read = open(root_dir + source_dir + section + ".tex", 'r')
            subsections = {}
            add_subsubsections = test_paragraph(section)
            while line := file_read.readline():
                if search_word_in_line("\section", line):
                    key = line.split("{")[1].split("}")[0]
                    key = test_latex_title(key)
                if search_word_in_line("\subsection", line):
                    subsection = line.split("{")[1].split("}")[0]
                    subsection = test_latex_title(subsection)
                    subsections[subsection] = []
                if search_word_in_line("\subsubsection", line):
                    subsubsection = line.split("{")[1].split("}")[0]
                    subsubsection = test_latex_title(subsubsection)
                    if add_subsubsections:    
                        subsections[subsection].append(subsubsection)
                    
            sections[key] = subsections
        else:
            key = empty_sections.pop(0)
            key = test_latex_title(key)
            sections[key] = None

    return sections

# create the nav.adoc file
def create_nav_file(section_files,sections):
    # create the nav.adoc file
    nav_file = result_dir + "nav.adoc"
    file_write = open(nav_file, 'w')

    file_write.write(":stem: latexmath\n")
    file_write.write("* xref:main_page.adoc[PhiFEM project]\n")

    for i,(section,subsections) in enumerate(sections.items()):        
        if section_files[i]!="":
            section_file_name = section_files[i].split("/")[1]
            file_write.write("** xref:" + section_file_name + ".adoc[" + section + "]\n")
            if subsections!=None:
                for j,(subsection,subsubsections) in enumerate(subsections.items()):
                    file_write.write("*** xref:" + section_file_name + "/subsec_" + str(j) + ".adoc[" + subsection + "]\n")
                    if len(subsubsections)!=0:
                        for k,subsubsection in enumerate(subsubsections):
                            file_write.write("**** xref:" + section_file_name + "/subsec_" + str(j) + "_subsubsec_" + str(k) + ".adoc[" + subsubsection + "]\n")
        else:
            section_file_name = "section_" + str(i)
            file_write.write("** xref:" + section_file_name + ".adoc[" + section + "]\n")

    file_write.close()

# create all directories and files of the documentation
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
                for j,(subsection,subsubsections) in enumerate(subsections.items()):
                    subsection_file = open(page_dir + section_file_name + "/subsec_" + str(j) + ".adoc", 'w')
                    subsection_file.write("= " + subsection + "\n")
                    subsection_file.close()
                    if len(subsubsections)!=0:
                        for k,subsubsection in enumerate(subsubsections):
                            subsubsection_file = open(page_dir + section_file_name + "/subsec_" + str(j) + "_subsubsec_" + str(k) + ".adoc", 'w')
                            subsubsection_file.write("= " + subsubsection + "\n")
                            subsubsection_file.close()
                    
            section_file.close()
        else:
            section_file_name = "section_" + str(i)
            section_file = open(page_dir + section_file_name + ".adoc", 'w')
            section_file.write("= " + section + "\n")
            section_file.close()     

# create the main page of the documentation
def create_main_page_file(section_files,sections):
    # create the nav.adoc file
    main_page_file = page_dir + "main_page.adoc"
    file_write = open(main_page_file, 'w')

    file_write.write("# Phi-FEM Project\n\n")
    file_write.write("The features include\n\n")

    for i,(section,subsections) in enumerate(sections.items()):        
        if section_files[i]!="":
            section_file_name = section_files[i].split("/")[1]
            file_write.write("** xref:" + section_file_name + ".adoc[" + section + "]\n")
        else:
            section_file_name = "section_" + str(i)
            file_write.write("** xref:" + section_file_name + ".adoc[" + section + "]\n")

    file_write.close()   

# copy all the images of the tex report in the antora documentation
def cp_images():       
    if os.path.exists(images_dir):
        shutil.rmtree(images_dir)
    shutil.copytree(root_dir + source_dir + "images/", images_dir)

# Test if there is a refernce to a figure in the line (many configurations possibles)
def test_fig(line):
    possible_ref = ["Figure \\ref","Figure~\\ref","Fig \\ref","Fig~\\ref","Fig.~\\ref","Fig.\\ref"]
    for ref in possible_ref:
        if search_word_in_line(ref,line):
            return ref,True
    return None,False

# Test if there is a refernce to a section in the line (many configurations possibles)
def test_section(line):
    possible_ref = ["Section \\ref","Section~\\ref","Sec \\ref","Sec~\\ref","Sec.~\\ref","Sec.\\ref"]
    for ref in possible_ref:
        if search_word_in_line(ref,line):
            return ref,True
    return None,False

# create a 
def get_label_sections(section_files):
    label_sections = {}
    for (s,(section,subsections)) in enumerate(sections.items()):
        section_file = section_files[s]
        if section_file!="":
            section_file_name = section_file.split("/")[1]
            file_read = open(root_dir + source_dir + section_file + ".tex", 'r')
            
            num_subsection = -1
            while line := file_read.readline():
                if search_word_in_line("\section", line):
                    if search_word_in_line("\label", line):
                        label_sections[line.split("\label{")[1].split("}")[0]]={"xref":[section_file_name,section]}
                
                if search_word_in_line("\subsection", line):
                    num_subsection += 1
                    subsection_name = line.split("{")[1].split("}")[0]
                    if search_word_in_line("\label", line):
                        label_sections[line.split("\label{")[1].split("}")[0]]={"xref":[section_file_name+"/subsec_"+str(num_subsection),subsection_name]}

                if search_word_in_line("\subsubsection", line):
                    if search_word_in_line("\label", line):
                        subsubsection_name = line.split("{")[1].split("}")[0]
                        subsubsection_name = subsubsection_name.replace(" ","_")
                        subsubsection_name = "_"+subsubsection_name.lower()
                        label_sections[line.split("\label{")[1].split("}")[0]]={"":subsubsection_name}

    return label_sections

def cp_section(section_file,sections,label_sections):
    file_read = open(root_dir + source_dir + section_file + ".tex", 'r')
    
    name_section_file = section_file.split("/")[1]
    file_write = open(page_dir + name_section_file + ".adoc", 'w')
    
    num_subsection = -1
    subsection_file = None
    while line := file_read.readline():
        if search_word_in_line("\section", line):
            section = line.split("{")[1].split("}")[0]
            section = test_latex_title(section)
            subsections = sections[section]
            file_write.write(":stem: latexmath\n")
            file_write.write(":xrefstyle: short\n")
            file_write.write("= " + section + "\n")
            line = ""

        if search_word_in_line("\subsection", line):
            num_subsection += 1
            num_subsubsection = -1

            if num_subsection==0 and subsections!=None:
                file_write.write("\n---\n")
                file_write.write("The features include\n\n")
                section_file_name = section_file.split("/")[1]
                for i,subsection_ in enumerate(subsections):
                    file_write.write("** xref:" + section_file_name + "/subsec_"+ str(i) + ".adoc[" + subsection_ + "]\n\n")

            subsection_file = "subsec_" + str(num_subsection) + ".adoc"
            file_write = open(page_dir + name_section_file + "/" + subsection_file, 'w')

            subsection = line.split("{")[1].split("}")[0]
            subsection = test_latex_title(subsection)
            subsubsections = subsections[subsection]
            file_write.write(":stem: latexmath\n")
            file_write.write(":xrefstyle: short\n")
            file_write.write("= " + subsection + "\n")
            line=""
        
        if search_word_in_line("\subsubsection", line):
            num_subsubsection += 1
            name_subsubsection = line.split("{")[1].split("}")[0]
            name_subsubsection = test_latex_title(name_subsubsection)
            if subsubsections!=[]:
                if num_subsubsection==0:
                    file_write.write("\n---\n")
                    file_write.write("The features include\n\n")
                    section_file_name = section_file.split("/")[1]
                    for i,subsubsection_ in enumerate(subsubsections):
                        file_write.write("** xref:" + section_file_name + "/subsec_"+ str(num_subsection) + "_subsubsec_" + str(i) + ".adoc[" + subsubsection_ + "]\n\n")

                subsubsection_file = "subsec_" + str(num_subsection) + "_subsubsec_" + str(num_subsubsection) + ".adoc"
                file_write = open(page_dir + name_section_file + "/" + subsubsection_file, 'w')
                subsubsection = line.split("{")[1].split("}")[0]
                file_write.write(":stem: latexmath\n")
                file_write.write(":xrefstyle: short\n")
                file_write.write("= " + subsubsection + "\n")
                line = "= " + name_subsubsection + "\n"
            else:
                line = "== " + name_subsubsection + "\n"

        if search_word_in_line("\paragraph", line):
            name_paragraph = line.split("{")[1].split("}")[0]
            name_paragraph = test_latex_title(name_paragraph)
            line = "== " + name_paragraph + "\n"

        if search_word_in_line("\graphicspath", line):
            line = ":imagesdir: \{moduledir\}/assets/" + line.split("{")[2].split("}")[0] + "\n"

        if search_word_in_line("\modif", line):
            sentence = line.split("\modif")[1].split("{")[1].split("}")[0]
            to_replace = "\modif{" + sentence + "}"
            line = line.replace(to_replace, "#" + sentence + "#")

        if search_word_in_line("$",line):
            tab_line = line.split("$")
            start_stem = 0
            line_modif = ""
            for i,part in enumerate(tab_line):
                line_modif += part
                if start_stem==0 and i!=len(tab_line)-1:
                    line_modif += "stem:["
                    start_stem = 1
                elif start_stem==1 and i!=len(tab_line)-1:
                    line_modif += "]"
                    start_stem = 0
            line = line_modif

        if search_word_in_line("\\begin{figure}", line):
            while not search_word_in_line("\end{figure}", line):
                line = file_read.readline()
                if search_word_in_line("\includegraphics", line):
                    image_name = line.split("{")[1].split("}")[0]
                    image_name = image_name[1:-1]   

                    linewidth = line.split("width=")[1].split("\\linewidth")[0]
                    if linewidth=="":
                        linewidth="1.0"
                    linewidth = float(linewidth)

                    width = linewidth * 600
                    height = linewidth * 480

                if search_word_in_line("\caption", line):
                    caption = line.split("{")[2].split("}")[0]

                if search_word_in_line("\label", line):
                    label = line.split("{")[1].split("}")[0]
                    file_write.write("[["+label+"]]\n")

            line = "."+caption+"\nimage::" + name_section_file + "/" + image_name + "[width="+str(width)+",height="+str(height)+"]\n"

        if search_word_in_line("\\begin{equation", line):
            line = "[stem]\n++++\n"
        
        if search_word_in_line("\end{equation", line):
            line = "++++\n"

        if search_word_in_line("\\begin{align*}", line) or search_word_in_line("\\begin{align}", line):
            line = "[stem]\n++++\n\\begin{aligned}\n"

        if search_word_in_line("\end{align*}", line) or search_word_in_line("\end{align}", line):
            line = "\\end{aligned}\n++++\n"

        if search_word_in_line("\\begin{enumerate", line) or search_word_in_line("\end{enumerate", line):
            line = "\n"
        
        if search_word_in_line("\item",line):
            line = line.replace("\item", "* ")

        if search_word_in_line("\\begin{Rem",line):
            line = "\n[NOTE]\n====\n"

        if search_word_in_line("\\end{Rem",line):
            line = "====\n"

        ref,test= test_fig(line)
        if test:
            name_label_fig = line.split("\\ref{")[1].split("}")[0]
            line = line.replace(ref+"{"+name_label_fig+"}","<<"+name_label_fig+">>")

        ref,test = test_section(line)
        if test:
            name_label_sec = line.split("\\ref{")[1].split("}")[0]
            label = label_sections[name_label_sec]
            if "xref" in label:
                line = line.replace(ref+"{"+name_label_sec+"}","xref:"+label["xref"][0]+".adoc"+"[Section \""+label["xref"][1]+"\"]")
            else:
                line = line.replace(ref+"{"+name_label_sec+"}","<<"+label[""]+">>")

        if search_word_in_line("\\newpage",line):
            line=""

        if search_word_in_line("\_",line):
            line = line.replace("\_","_")

        while search_word_in_line("\href",line):
            url = line.split("{")[1].split("}")[0]
            text = line.split("{")[2].split("}")[0]
            line = line.replace("\href{"+url+"}{"+text+"}",url+"["+text+"]")

        while search_word_in_line("\\textbf",line):
            sentence = line.split("\\textbf")[1].split("{")[1].split("}")[0]
            line = line.replace("\\textbf{"+sentence+"}","*"+sentence+"*")

        while search_word_in_line("\\textit",line):
            sentence = line.split("\\textit")[1].split("{")[1].split("}")[0]
            line = line.replace("\\textit{"+sentence+"}","_"+sentence+"_")

        if search_word_in_line("\\begin{Prop}",line):
            if search_word_in_line("[",line):
                prop_title = line.split("[")[1].split("]")[0]
                line = "\n[]\n====\n*Propositon ("+prop_title+").*\n"
            else:
                line = "\n[]\n====\n*Propositon.*\n"

        if search_word_in_line("\\end{Prop}",line):
            line = "====\n"

        if search_word_in_line("\\begin{Def}",line):
            if search_word_in_line("[",line):
                def_title = line.split("[")[1].split("]")[0]
                line = "\n[]\n====\n*Definition ("+def_title+").*\n"
            else:
                line = "\n[]\n====\n*Definition.*\n"

        if search_word_in_line("\\end{Def}",line):
            line = "====\n"

        if search_word_in_line("\\begin{Example}",line):
                line = "\n---\n*Example.*\n"

        if search_word_in_line("\\end{Example}",line):
            line = "\n---\n"

        if line!="":
            while line[0]=="\t":
                line = line[1:]

            if line[0]!="%":
                file_write.write(line)
    
def cp_all_sections(section_files,sections):
    label_sections = get_label_sections(section_files)
    for i,(section,subsections) in enumerate(sections.items()):        
        if section_files[i]!="":
            cp_section(section_files[i],sections,label_sections)
        else:
            section_file_name = "section_" + str(i)
            file_write = open(page_dir + section_file_name + ".adoc", 'w')
            file_write.write("= " + section + "\n\n")
            file_write.write("#TO COMPLETE !#\n")
            file_write.close()

def rm_all():
    shutil.rmtree(page_dir)
    os.mkdir(page_dir)
    shutil.rmtree(images_dir)
    os.mkdir(images_dir)
    os.remove(result_dir + "nav.adoc")

# si il y a déjà un dossier antora, on le supprime et on copie le dossier antora_base
# rm_all()
section_files,empty_sections = get_section_files()
sections = get_sections(section_files,empty_sections)
create_nav_file(section_files,sections)
create_nav(section_files,sections)
create_main_page_file(section_files,sections)
cp_images()
cp_all_sections(section_files,sections)