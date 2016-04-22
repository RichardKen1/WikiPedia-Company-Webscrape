# snp-index.py - script that creates a text file with the links for each company
# For use in creating link matrix

import subprocess
import numpy
import sys
import re
from collections import *
import pywikibot
from sklearn.feature_extraction.text import TfidfVectorizer

files = []


def ngramMatrix():
    site = pywikibot.Site()
    page = pywikibot.Page(site, u"List of S&P 500 companies")
    text = page.text

    # Print (text)
    # Text is a string of the list of S&P 500 list on wiki

    upperPar = text.split("==Recent and announced changes to the list of S&P 500 Components")

    chart = upperPar[0].split("[[Central Index Key|CIK]]")[1]

    chart = chart.split("||")

    for i in range(len(chart)):
        chart[i] = chart[i].strip().replace("[[", "").replace("]]", "")
	
    counter = 0
    j=0
    names=list(range(len(range(1,len(chart),7))))
    sector=list(range(len(range(3,len(chart),7))))
    industry=list(range(len(range(4,len(chart),7))))
    location=list(range(len(range(5,len(chart),7))))

    j = 0
    i = 0

    # Fix company names
    for i in range(1,len(chart),7):
        site = pywikibot.Site()
        page = pywikibot.Page(site, chart[i])
        text= page.text
        if text != "" and text[0] == '#':
            first_half = text.split("[[")
            second_half = first_half[1].split("]]")
            text = second_half[0]
            text = text.strip()
            names[j]=text
        else:
            names[j]=chart[i]

        sector[j]=chart[i+2]
        industry[j]=chart[i+3]
        location[j]=chart[i+4]
        site = pywikibot.Site()
        page = pywikibot.Page(site, names[j])
        text = page.text
        if text != "":
            text = text.split("==")[0]
            names[j]=text
        else:
            names[j] = names[j]
        j = j + 1

    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform(names)

    matrix = ((tfidf * tfidf.T).A)

    length = len(matrix)
    for x in range(0, length):
        for y in range(0, length):
            if x == y:
                matrix[x, y] = 0

    normalize(matrix)

    return matrix


def createFiles():
    global files
    # Create a list of all company names in "names.txt"
    subprocess.check_output("python snp.py > names.txt", shell=True)

    # Create a separate file of links contained on the wikipedia page for each separate company

    i = 1

    with open("names.txt") as f:
        for line in f:
            files.append("links" + str(i) + ".txt")
            i = i + 1
            query = 'python pwb.py listpages -links:"%s" > %s' % (str(line), str(files[i - 2]))
            subprocess.check_output(query, shell=True)

    size = i - 1
    return size


def backMatrix(size):
    global files
    # Now we have created every text file
    # Create the 500 x 500 matrix (may be different depending on S&P size) and fill in values

    i = size

    matrix = numpy.zeros((i, i))

    j = 0

    for j in range(0, i):
        for k in range(j + 1, i):
            links = compare(files[j], files[k])
            matrix[j, k] = links
            matrix[k, j] = links

    normalize(matrix)

    return matrix


# Compares two text files for companies line by line counting number of shared lines
def compare(file1, file2):
    # Create a set of unique links
    links = set()

    # Number of links shared between the two companies
    shared = 0 

    # Go through each file line by line and determine which links are shared
    with open(file1) as f1, open(file2) as f2:
        for line in f1:
            line = line.strip()
            i = 0
            for char in line:
                if char == " ":
                    line = line[i + 1:]
                    break
                else:
                    i = i + 1
                    continue
            links.add(line)
        for line in f2:
            line = line.strip()
            i = 0
            for char in line:
                if char == " ":
                    line = line[i + 1:]
                    break
                else:
                    i = i + 1
                    continue
            if line in links:
                shared = shared + 1

    return shared


def normalize(matrix):
    length = len(matrix)
    for x in range(0, length):
        total = 0
        for y in range(0, length):
            total = total + matrix[x, y]
        for y in range(0, length):
            matrix[x, y] = matrix[x, y] / total


    return matrix


def combine(ngram, backlink):
    matrix = (0.3 * ngram) + (0.7 * backlink)
    normalize(matrix)

    return matrix


def returnMatrix():
    ngram = ngramMatrix()
    size = createFiles()
    backlink = backMatrix(size)
    finalMatrix = combine(ngram, backlink)

    return finalMatrix


if __name__ == '__main__':
    ngram = ngramMatrix()
    size = createFiles()
    backlink = backMatrix(size)
    finalMatrix = combine(ngram, backlink)

    print(finalMatrix)
