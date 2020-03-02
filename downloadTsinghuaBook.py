from selenium import webdriver
from time import sleep
import requests
import pickle
import os
import img2pdf
import re
import pathlib



bookid = 'bdeab318-1caf-443d-82e5-2b905cef6098'

book_url_template = 'http://reserves.lib.tsinghua.edu.cn/Search/BookDetail?bookId={}'
book_title = 'untitled'
base_dir = os.path.abspath(os.path.join('./tmp_dl', bookid))
pathlib.Path(base_dir).mkdir(parents=True, exist_ok=True)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-data-dir=selenium") 
chrome_options.add_experimental_option("prefs", {
  "download.default_directory": base_dir,
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True,
  "profile.default_content_setting_values.automatic_downloads": 1
})
driver = webdriver.Chrome(chrome_options=chrome_options)

def login():
    login_url = 'http://reserves.lib.tsinghua.edu.cn/Account/LogIn'
    driver.get(login_url)
    try:
        driver.find_element_by_id('i_user').send_keys('')
        driver.find_element_by_id ('i_pass').send_keys('')
        driver.find_element_by_xpath('//a[text()="登录"]').click()
    except:
        pass
    sleep(5)

def getBookDetail():
    global book_title
    book_url = book_url_template.format(bookid)
    driver.get(book_url)
    ele = driver.find_element_by_class_name('p-result')
    title_ele = ele.find_element_by_tag_name('table').find_elements_by_tag_name('b')[1]
    book_title = title_ele.text
    print(book_title)
    links_elements = ele.find_elements_by_tag_name('a')
    links_url = [e.get_attribute("href") for e in links_elements]
    links_url = [u.replace('index.html', 'HTML5/index.html') for u in links_url]
    
    return links_url

def downloadAllLinks(links):
    jpg_index = 0
    chp_index = 0
    print('{} chapters in all'.format(len(links)))
    for url in links:
        driver.get(url)
        print('Chapter: {}'.format(chp_index))
        chp_index+=1
        pageCnt = driver.find_element_by_id ('textfield').get_attribute('value')
        pageCnt = pageCnt.split('/')[-1]
        pageCnt = int(pageCnt)
        print('{} pages in this link'.format(pageCnt))
        jpg_url_template = url.replace('index.html','m/{}.jpg')
        for idx in range(1, pageCnt+1):
            jpg_url = jpg_url_template.format(idx)
            # driver.get(jpg_url)
            script_js = 'var dataURL = "{}";' \
                        'var link = document.createElement("a"); ' \
                        'link.download = "{}";' \
                        'link.href = dataURL;' \
                        'document.body.appendChild(link);' \
                        'link.click();' \
                        'document.body.removeChild(link);' \
                        'delete link;'.format( jpg_url, '{}.jpg'.format(jpg_index) )
            driver.execute_script(script_js)
            sleep(0.3)
            jpg_index +=1
            # confirm()
        # confirm()
        sleep(1)

def confirm():
    input('Press any key to continue...')


def makePdf():
    global book_title
    print('Making pdf...')
    # A4 paper
    a4inpt = (img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297))
    layout_fun = img2pdf.get_layout_fun(a4inpt)
    with open("{}.pdf".format(book_title), "wb") as f:
        files = [i for i in os.listdir(base_dir) if i.endswith(".jpg")]
        files.sort(key=lambda f: int(re.sub(r'\D', '', f)))
        files = [os.path.join(base_dir, f) for f in files]
        out = img2pdf.convert(files, layout_fun=layout_fun)
        f.write(out)


if __name__ == "__main__":
    login()
    links_url = getBookDetail()
    downloadAllLinks(links_url)
    makePdf()
    confirm()
