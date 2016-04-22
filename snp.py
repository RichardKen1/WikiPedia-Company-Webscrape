import pywikibot

site = pywikibot.Site()
page = pywikibot.Page(site, u"List of S&P 500 companies")
text = page.text


#print (text)
# text is a string of the list of S&P 500 list on wiki


upperPar = text.split("==Recent and announced changes to the list of S&P 500 Components")

chart = upperPar[0].split("[[Central Index Key|CIK]]")[1]



chart = chart.split("||")

for i in range(len(chart)):
	chart[i] = chart[i].strip().replace("[[", "").replace("]]", "")
	


counter = 0
j=0
names=list(range(len(range(1,len(chart),7))))

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
    print (names[j])
    j+=1
