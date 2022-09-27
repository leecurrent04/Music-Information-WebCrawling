from selenium import webdriver
from bs4 import BeautifulSoup as bs
from requests import get
import os

# You must modify driver_path!
# https://sites.google.com/chromium.org/driver/
driver_path = "./chromedriver_linux64/chromedriver"
url = input("URL: ")
# url = "https://vibe.naver.com/album/123450"


driver = webdriver.Chrome(driver_path)
driver.get(url)

html = driver.page_source
soup = bs(html,'lxml')

# find album title
album_title = soup.findAll('span',attrs={"class":"title"})[0].get_text()
if not os.path.exists("./%s"%album_title):
    os.mkdir("./%s"%album_title)

# find group name
group_name = soup.findAll('a',attrs={"class":"link_sub_title"})[0].get_text()

# find album date
album_info = soup.findAll('div',attrs={"class":"sub"})[0].findAll('span')
album_date = album_info[0].get_text().split('.')[0]
album_genre = album_info[1].get_text()
#print(album_date,album_genre)

# find album img
album_img = soup.findAll('div',attrs={"class":"summary_thumb"})[0]
tmp_album_url = album_img.find("img").get("src").split("?")[0]

with open("./%s/img.jpg"%(album_title),"wb") as file:
    response = get("%s?type=r1440Fll"%tmp_album_url)
    file.write(response.content)

with open("./%s/img_raw.jpg"%(album_title),"wb") as file:
    response = get(tmp_album_url)
    file.write(response.content)

# save
with open("./%s/data.txt"%album_title,"w") as file:
    # find music name list
    music_lists = soup.findAll('td',attrs={"class":"song"})

    for music_list in music_lists:
        title = music_list.find("a").get("title")
        music_url = music_list.find("a").get("href")
        #print(title,"https://vibe.naver.com%s"%music_url)

        file.write("%s,%s,%s,%s,%s,"%(title,group_name,album_title,album_date,album_genre))

        # get each music data
        music_driver = webdriver.Chrome(driver_path)
        music_driver.get("https://vibe.naver.com%s"%music_url)
        music_soup = bs(music_driver.page_source,'lxml')

        # person
        music_infos = music_soup.findAll('div',attrs={"class":"song_info"})[0].get_text()
        file.write("{%s},"%(music_infos))

        # lyrics
        music_lyrics = music_soup.findAll('div',attrs={"class":"lyrics hide"})

        if music_lyrics:
            #print(music_lyrics)
            file.write("\n%s\n\n\n\n"%music_lyrics[0].get_text())
        else: file.write("\n\n\n")

        music_driver.close()

driver.quit()