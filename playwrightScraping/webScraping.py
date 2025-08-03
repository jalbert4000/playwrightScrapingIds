"""
Actual           : 2025-08-02  ---> 02 de Agosto del 2025
En la consola    : python3 manage.py runserver 
En el navegador. : http://127.0.0.1:8000
Web driver       : No es necesario, se utiliza Playwright
Version navegador: Chromium
En el input      : CATG10197,CATG24316,CATG20279,CATG20268,CATG24462
Cookies          : No crear el file solo se crea y guarda la cookies en la ruta raiz  --->  path="estado_sesion.json"
File             : Podemos llevarnos los archivos de session creados y reutilizar los cookies para cargar la session
"""

import asyncio
from playwright.async_api import async_playwright

class WebScraping():
    
    #Inicializo los atributos (constructor)
    def __init__(self,tipoNavegador):

        try:
            self.tipoNavegador=tipoNavegador
        except Exception as error:
            print("Ha ocurrido un error", type(error).__name__, "–", error)

    #Metodo para ejecutar el scraping 
    def execute(self, categoriasLista=[],tipoUrl=''):
        try:
            categoriasOK, categoriasNOEX = asyncio.run(self.extraer_libros(categoriasLista,tipoUrl))
            return (categoriasOK, categoriasNOEX)

        except KeyboardInterrupt:
            print("*** Stop web scraping ***")
            exit(1)

    #Metodo asincrono para extraer datos de la web
    async def extraer_libros(self, categoriasLista,tipoUrl):

        categoriasOK = []
        categoriasNOEX = []
        async with async_playwright() as p:
            
            #Configuro el navegador - True: No mostrar navegador, False: Mostrar navegador
            browser = await p.chromium.launch(headless=False)
            #Cargo en el navegador la sesion guardada de la plataforma - session/cookies
            context = await browser.new_context(storage_state="estado_sesion.json")
            #Abro una nueva pestaña en el navegador
            page = await context.new_page()
            
            try:
                await page.goto("https://admin.fazil.services/application/catalog/taxonomy/categories")
                await page.locator('.nice-button').click()
                #print("Ingreso a la sesión exitoso.")
                await asyncio.sleep(3)

                #Espera a que se cargue el iframe de la plataforma
                await page.wait_for_selector("#extension-iframe", timeout=30000)
                frame_locator = page.frame_locator("#extension-iframe")
                if frame_locator is None:
                    print("No se encontró el iframe.")
                    categoriasOK.append("No se encontró el iframe.")
                #print("...Ingresando a Iframe...")
                await frame_locator.locator("#search-category").wait_for(timeout=10000)
                await frame_locator.locator("//div[text()='Ver nivel por nivel']").click()
                await frame_locator.locator("//div[text()='Ver todas las categorías']").click()
                #print("...Cargando categorías...")
                await asyncio.sleep(3)
                
                #Recorro la lista de categorías y realizo la búsqueda
                for item in categoriasLista:

                    #print(f"...Buscando categoría: {item}")
                    #await asyncio.sleep(2)
                    await frame_locator.locator("#search-category").fill(item)
                    await asyncio.sleep(3)

                    categoria = await frame_locator.locator('//*[@id="root"]/div/div/div[4]/div/div/div[4]/div[2]/table/tbody/tr[1]/td[2]').inner_text()
                    catIdPadre = await frame_locator.locator('//*[@id="root"]/div/div/div[4]/div/div/div[4]/div[2]/table/tbody/tr[1]/td[5]').inner_text()
                    catIdHijo = item
                    idPadrePosInicial = catIdPadre.find("(") + 1
                    idPadrePosFinal = catIdPadre.find(")")
                    categoriaClear = categoria.replace(' ','')
                    #print("...dato traido!")
                    #print(categoria)
                    #print(catIdPadre)

                    if tipoUrl == 'api':
                        deeplinkUrl = "https://api.test.tottus.cl/categories?name=" + categoriaClear.replace(',','') + "&id=" + catIdHijo + "&landingtonewPLP=true&defaultSelectParentId=" + catIdPadre[idPadrePosInicial:idPadrePosFinal] + "&defaultSortBy=Recomendados"
                        deeplink = deeplinkUrl + '\n'
                    elif tipoUrl == 'excel':
                        deeplinkCat = categoria
                        deeplinkUrl = deeplinkCat + '\n' + "https://www.tottus.com/categories?name=" + categoriaClear.replace(',','') + "&id=" + catIdHijo + "&landingtonewPLP=true&defaultSelectParentId=" + catIdPadre[idPadrePosInicial:idPadrePosFinal] + "&defaultSortBy=Recomendados"
                        deeplink = deeplinkUrl + '\n'
                    elif tipoUrl == 'deeplink':
                        deeplinkCat = "Categoría: " + categoria
                        deeplinkId = "ID: " + catIdHijo
                        deeplinkUrl = "https://www.tottus.com/categories?name=" + categoriaClear.replace(',','') + "&id=" + catIdHijo + "&landingtonewPLP=true&defaultSelectParentId=" + catIdPadre[idPadrePosInicial:idPadrePosFinal] + "&defaultSortBy=Recomendados"
                        deeplink = deeplinkCat + '\n' + deeplinkId + '\n' + deeplinkUrl + '\n \n'
                    elif tipoUrl == 'web':
                        deeplinkId = "ID: " + catIdHijo
                        deeplinkUrl = "https://www.tottus.cl/tottus-cl/lista/" + catIdHijo + "/" + categoria.replace(' ','-')
                        deeplink = deeplinkId + '\n' + deeplinkUrl + '\n \n'
                    else:
                        deeplinkUrl = "https://api.test.tottus.cl/categories?name=" + categoriaClear.replace(',','') + "&id=" + catIdHijo + "&landingtonewPLP=true&defaultSelectParentId=" + catIdPadre[idPadrePosInicial:idPadrePosFinal] + "&defaultSortBy=Recomendados"
                        deeplink = deeplinkUrl + '\n'

                    categoriasOK.append(deeplink)
                    
            except Exception as e:
                print("Error durante el login:", e)
                categoriasNOEX.append("Error durante el login")
            
            #print("...aaaa!")
            await asyncio.sleep(2)
            #print("...loco!")
            await browser.close()

        return categoriasOK, categoriasNOEX