# FIXME: This scraper is not yet implemented

async def is_halova_or_jungmannova_url(session, url: str):
    soup = await _get_soup(session, url)
    stop_name = soup.css.select("#stop-name")
    if stop_name:
        stop_name = stop_name[0].text.strip().lower()
        if stop_name == "hálova" or stop_name == "jungmannova":
            print(url)
            return True

async def print_halova_id_asynchronously(input_data_list):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(is_halova_or_jungmannova_url(session, url)) for url in input_data_list]
        await asyncio.gather(*tasks)



#####################################################################################################
    # 16.3.2024 IMHD Zastavkova tabula - ideme zistit id zastavky Halova a Jungmannova:

    zast_tabula_url = "https://imhd.sk/ba/online-zastavkova-tabula?theme=white&zoom=67&fullscreen=0&nthDisplay=0&minDisp=0&detectIdle=0&showClock=0&showInfoText=0&st="
    # input_data = [zast_tabula_url + str(number) for number in range(50)]
    # input_data = [zast_tabula_url + str(number) for number in range(50, 100)]
    input_data = [zast_tabula_url + str(number) for number in range(100, 150)]
    # input_data = [zast_tabula_url + str(number) for number in range(150, 200)]
    # input_data = [zast_tabula_url + str(number) for number in range(200, 250)]
    # input_data = [zast_tabula_url + str(number) for number in range(250, 300)]
    # input_data = [zast_tabula_url + str(number) for number in range(300, 350)]
    # input_data = [zast_tabula_url + str(number) for number in range(350, 400)]


    import asyncio
    # asynchronously scrap imhd.sk

    asyncio.run(print_halova_id_asynchronously(input_data))