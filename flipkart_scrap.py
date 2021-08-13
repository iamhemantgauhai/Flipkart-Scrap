from selenium import webdriver
import time,os, requests, pprint,json, concurrent.futures
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool

prouct_info=[]

def description_return(url): #This function will hit the product URL and return its description by bs4
    req=requests.get(url)
    html_cont=req.content
    soup_d=BeautifulSoup(html_cont,'html.parser')
    try:
        description=soup_d.find('div',class_='_1mXcCf RmoJUa').text.strip()
        return description
    except:
        return 'N/A'


def scraper_by_url(URL): #This is data Scraper
    r=requests.get(URL)
    soup=BeautifulSoup(r.content,'html.parser')
    products_list=soup.find_all('div',{'class':'_3pLy-c row'}) #To get list of all detail of all products
    url_prod_list=soup.find_all('a',class_='_1fQZEK') #To get list of products URL
    prod_num_list=[x for x in range(len(url_prod_list))]
    threads_count=len(url_prod_list)
    def scraper_by_prod_num(prod_num):
        elem_dict={}
        spec_dict={}
        name_prod=products_list[prod_num].find('div',class_='_4rR01T').text #NAME
        price_prod='Rs. '+products_list[prod_num].find('div',class_='_30jeq3 _1_WHN1').text.encode('ascii','ignore').decode() #PRICE
        rating=products_list[prod_num].find('div',class_='_3LWZlK').text #RATING
        prod_url='https://www.flipkart.com'+url_prod_list[prod_num]['href'] #PRODUCT URL TO GET IT'S DESCRIPTION
        ram_info=(products_list[prod_num].find('ul',class_='_1xgFaf').li.text.strip()).split('|')[0] #RAM INFO
        description=description_return(prod_url) #DESCRIPTION BOX
        spec_dict['Price']=price_prod
        spec_dict['RAM']=ram_info
        spec_dict['Rating']=rating
        spec_dict['URL']=prod_url
        spec_dict['Description']=description
        elem_dict[name_prod]=spec_dict
        prouct_info.append(elem_dict)
        print(f'Product {prod_num+1} added')
    with ThreadPool(threads_count) as pool:
        pool.map(scraper_by_prod_num,prod_num_list)

def url_list_creator(main_url,page_count): #To Navigate Pages
    print(f'We have {page_count} pages here')
    page_inp=int(input('How many pages to scrape ? :  '))
    url_list=[]
    url_list.append(main_url)
    print('URL of Page 1 added')
    if page_inp!=1:
        for page_no in range(2,page_inp+1):
            next_url=main_url+f'&page={page_no}'
            url_list.append(next_url)
            print(f'URL of Page {page_no} added :-)')
    return url_list


def main_function():
    driver_path=os.path.join(os.getcwd(),'chromedriver')
    driver=webdriver.Chrome(driver_path)
    flipkart='https://www.flipkart.com/'
    driver.get(flipkart)
    try: #To handle Login Pop-Up
        login_pop=driver.find_element_by_xpath('/html/body/div[2]/div/div/button')
        login_pop.click()
        print('Popup closed :-)')
    except:
        print('Did not get any popup')
    time.sleep(2)
    search_field=driver.find_element_by_xpath('//*[@id="container"]/div/div[1]/div[1]/div[2]/div[2]/form/div/div/input')
    search_field.send_keys('android mobiles'+'\n')
    time.sleep(5)
    brand_list=['Redmi','oppo']
    brand_search_filed=driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[2]/div[1]/div[1]/div/div[1]/div/section[5]/div[2]/div[1]/div[1]/input')
    for brand_number in range(len(brand_list)):
        brand_search_filed.clear()
        brand_search_filed.send_keys(brand_list[brand_number]+'\n')
        time.sleep(0.5)
        if brand_number==0:
            driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[2]/div[1]/div[1]/div/div[1]/div/section[5]/div[2]/div[1]/div[2]').click()
        else:
            driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[2]/div/div[1]/div/div[1]/div/section[5]/div[2]/div[1]/div[3]').click()
        time.sleep(3)

 
    page_count=int((driver.find_element_by_xpath('//*[@id="container"]/div/div[3]/div[2]/div/div[2]/div[26]/div/div/span[1]').text.split())[3]) #To get total number of pages
    main_url=driver.current_url #To get LIVE URL 
    driver.close()
    url_list=url_list_creator(main_url,page_count)
    return url_list

def soup_passer(url_list):
    threads=len(url_list)
    print(threads,' Launched')
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(scraper_by_url,url_list)
    
        
if __name__ == "__main__":
    url_list=main_function()
    initial_time=time.time()
    soup_passer(url_list)
    t_after=time.time()
    print(f'Data Scraped in {t_after-initial_time} seconds')
    f=open('flip_scrap.json','w')
    json.dump(prouct_info,f,indent=2)
    print(len(prouct_info))