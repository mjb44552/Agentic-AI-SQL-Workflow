
from bs4 import BeautifulSoup

file = 'Web_Scraping\crested_butte_practice.html'
with open(file) as fp:
    soup = BeautifulSoup(fp,'html.parser')

main_content = soup.find(id='main-content')

lift_table = main_content.find('div',class_ = 'lift-table')
print(lift_table.contents[0].contents[0].find('span', class_ = 'lift-number').contents[0])
# for child in lift_table.children:
#     print(child)

#print(lift_table.contents)
# lift_header = lift_table.

#print(main_content.contents)

# for child in main_content.children:
#     print(child)

#print(soup)

