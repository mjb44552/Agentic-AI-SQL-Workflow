
from bs4 import BeautifulSoup

file = 'crested_butte_practice_files.html'
with open(file) as fp:
    soup = BeautifulSoup(fp,'html.paser')

print(soup)