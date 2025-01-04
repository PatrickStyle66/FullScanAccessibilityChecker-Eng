import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
import streamlit as st
import requests
ScoresTable = {'Página':[],'Pontuação':[], 'Link':[]}
firstPage = True
count, finalScore,pageCount = 0, 0, 0
placeholder = st.empty()
imagesList = {}
overviewList= {}
scoreList = {}
infoList = {}
repeatList = []
def getPageScore(html,site = ''):
    global driver, actions
    practicesList = []
    tableList = []
    info = []
    driver.switch_to.window(driver.window_handles[1])
    driver.get('https://accessmonitor.acessibilidade.gov.pt/')
    HtmlMode = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[contains(@data-rr-ui-event-key,"tab2")]')))
    HtmlMode.click()
    search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "html")))
    search.clear()
    if firstPage:
        driver.switch_to.window(driver.window_handles[0])
        pyperclip.copy(driver.page_source)
        site = html
    else:
        pyperclip.copy(html)
    driver.switch_to.window(driver.window_handles[1])
    search.send_keys(Keys.CONTROL, 'v')
    sendButton = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[contains(@id,"btn-html")]')))
    sendButton.click()
    try:
        score = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, "svg")))
        scoreImage = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"d-flex flex-row mt-5 mb-5 justify-content-between container_uri_chart")]')))
        actions.move_to_element(scoreImage).perform()
        scoreImage = scoreImage.screenshot_as_png
        score = str(score.text).split('\n')[1]
        results = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//table[contains(@class,"table table_primary ")]//tbody//tr')))
        infoElements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class,"size_container d-flex flex-column gap-4")]//div[contains(@class,"d-flex flex-column")]')))
        for element in infoElements:
            actions.move_to_element(element).perform()
            info.append(element.screenshot_as_png)
        title = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//tr[contains(@class,"mobile_table")]')))
        actions.move_to_element(title).perform()
        title = title.screenshot_as_png
        tableList.append(title)
        tableElements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//table[contains(@class,"table table-bordereds table-alternative ")]//tbody//tr')))
        for element in tableElements:
            actions.move_to_element(element).perform()
            tableList.append(element.screenshot_as_png)
        for element in results:
            actions.move_to_element(element).perform()
            practicesList.append(element.screenshot_as_png)
        if firstPage:
            ScoresTable['Página'].append('Início')
            ScoresTable['Link'].append(site)
            imagesList['Início'] = practicesList
            scoreList['Início'] = scoreImage
            overviewList['Início'] = tableList
            infoList['Início'] = info
        else:
            driver.switch_to.window(driver.window_handles[2])
            if driver.title in imagesList.keys():
                repeatList.append(driver.title)
                repeat = repeatList.count(driver.title) + 1
                repeatTitle =f'{driver.title}-{repeat}'
                ScoresTable['Página'].append(repeatTitle)
                ScoresTable['Link'].append(site)
                imagesList[repeatTitle] = practicesList
                scoreList[repeatTitle] = scoreImage
                overviewList[repeatTitle] = tableList
                infoList[repeatTitle] = info
            else:
                ScoresTable['Página'].append(driver.title)
                ScoresTable['Link'].append(site)
                imagesList[driver.title] = practicesList
                scoreList[driver.title] = scoreImage
                overviewList[driver.title] = tableList
                infoList[driver.title] = info

        print(f'score da página: {score}')
        return float(score)
    except Exception as error:
        if firstPage:
            return -1
        print(error)
        return 0

def getLinkFromElement(item):
    try:
        return item.get_attribute("href")
    except:
        pass

def queryString(site):
    return f'//a[(contains(@href, "{site}") or starts-with(@href, "/") or starts-with(@href, "#")) and not(contains(@href,"jpg") or contains(@href,"youtube") or contains(@href,"youtu.be") or contains(@href,"instagram") or contains(@href,"facebook") or contains(@href,"linkedin") or contains(@href,"tiktok") or contains(@href,"mailto") or contains(@href,"jpeg") or contains(@href,"png") or contains(@href,"mp3") or contains(@href,"twitter") or contains(@href,"x.com") or contains(@href,"google") or contains(@href,"wikipedia") or contains(@href,"pdf") or contains(@href,"JPEG") or contains(@href,"PNG")or contains(@href,"JPG") or contains(@href,"PDF"))]'

def searchThroughWebsite(linkList,site):
    global placeholder,pageCount,AnalyzedSite, driver
    removeList = []
    for link in linkList:
        try:
            req = requests.get(link)
            print(req.status_code)
        except:
            continue
        if req.status_code == 200 and link != site:
            driver.get(link)
            current_url = driver.current_url
            if site not in current_url:
                removeList.append(link)
                continue
            try:
                AnalyzedSite.markdown(f"### procurando mais páginas em {link}")
                elementList = WebDriverWait(driver, 0.5).until(
                    EC.presence_of_all_elements_located((By.XPATH,queryString(site))))
            except:
                continue
            FoundLinks = set(map(getLinkFromElement, elementList))
            linkSet = set(linkList)
            FoundLinks = list(FoundLinks - linkSet)
            linkList.extend(FoundLinks)
            print(f'links novos encontrados:{len(FoundLinks)} links totais assimilados: {len(linkList)}')
            pageCount = len(linkList) - len(removeList)
            placeholder.markdown(f"### :blue-background[Procurando Páginas: {pageCount + 1}  :mag_right: ]")
    for item in removeList:
        try:
            linkList.remove(item)
        except:
            continue
    return linkList


def getWebsiteScores(site):
    global count, finalScore, placeholder, AnalyzedSite, driver
    print("Iniciando Análise...")

    try:
        driver.switch_to.window(driver.window_handles[0])
        driver.get(site)
        site = driver.current_url
        print(f'domínio real: {site}')
    except:
        print("Site não encontrado.")
        AnalyzedSite.markdown("### Site não encontrado, Recarregue a página e tente novamente")
        driver.quit()
        return

    points = 0
    AnalyzedSite.markdown(f"### Analisando página inicial {site}")
    result = getPageScore(site)
    if result == -1:
        return result
    driver.switch_to.window(driver.window_handles[0])
    print(result)
    if result != 0:
        ScoresTable['Pontuação'].append(result)
        points += result
        count += 1
    WebDriverWait(driver, 0.1)
    elementList = driver.find_elements(By.XPATH, queryString(site))
    print(elementList)
    linkList = list(set(map(getLinkFromElement,elementList)))
    driver.switch_to.window(driver.window_handles[2])
    linkList = searchThroughWebsite(linkList,site)
    driver.switch_to.window(driver.window_handles[0])
    for item in linkList:
       placeholder.markdown(f"### :blue-background[Páginas encontradas: {len(linkList) + 1}     Páginas analisadas: {count} :hourglass_flowing_sand: ]")
       try:
           global firstPage
           firstPage = False
           print(item)
           if item == site:
               continue
           driver.switch_to.window(driver.window_handles[2])
           driver.get(item)
           html = driver.page_source
           AnalyzedSite.markdown(f"### Analisando {item}")
           result = getPageScore(html,site=item)
           driver.switch_to.window(driver.window_handles[0])
           if result != 0:
               ScoresTable['Pontuação'].append(result)
               print(result)
               points += result
               count += 1

       except Exception as error:
           print(error)
           continue
    if count == 0:
        finalScore = 0
    else:
        finalScore = points / count
    print(f"Média: {finalScore}")
    print(f"Páginas Verificadas: {count}")
    print(ScoresTable)
    df = pd.DataFrame(data=ScoresTable)
    df2 = df.dropna()
    df2.to_csv(f"{site.split('.')[1]}.csv")
    driver.quit()
    return df2

@st.fragment
def imageSlider():
    sliderPlaceholder = st.empty()
    with sliderPlaceholder.container():
        image = st.selectbox("Página", imagesList.keys())
        left_co, cent_co, last_co = st.columns(3)
        with left_co:
            for element in infoList[image]:
                st.image(element)
        with cent_co:
            st.image(scoreList[image],use_column_width=False)
        for element in overviewList[image]:
            st.image(element)
        for element in imagesList[image]:
            st.image(element)


def main():
    global placeholder, AnalyzedSite, driver, actions
    st.title("FullScan Accessibility Checker")
    st.subheader("Verificador de Acessibilidade")
    message = st.empty()
    message.header("Digite o site a ser analisado")
    AnalyzedSite = st.empty()
    site = AnalyzedSite.text_input("ex: https://site .com .br")
    print(site)
    if site and site != '':
        driver = webdriver.Edge()
        driver.set_window_position(-10000, 0)
        driver.set_window_size(1920, 1080)
        driver.switch_to.new_window('tab')
        driver.switch_to.new_window('tab')
        actions = ActionChains(driver)
        with st.spinner("Analisando Páginas...  "):
            results = getWebsiteScores(site)
            if results is int:
                st.header('Não foi possível analisar o site devido a um erro no access monitor. Recarregue a página e tente outro site')
            else:
                if count > 0:
                    st.header(f"Páginas Totais Analisadas: {count} :white_check_mark:")
                if finalScore != 0:
                    if finalScore >= 8:
                        st.header(f"Média geral: :green[{finalScore:.2f}]")
                    elif finalScore >= 6:
                        st.header(f"Média geral: :orange[{finalScore:.2f}]")
                    else:
                        st.header(f"Média geral: :red[{finalScore:.2f}]")
                    st.write(results)
                    placeholder.empty()
                    message.header("Recarregue a página para uma nova consulta")
                    AnalyzedSite.empty()
                    st.header("Relatório por página")

    if imagesList:
        imageSlider()


main()
