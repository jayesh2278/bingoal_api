import scrapy
import json

class ExampleSpider(scrapy.Spider):
    name = "example"
    # start_urls = ["https://resources.bingoal.be//generated/uof/sportLiveMenu_1_1.json?k=8758&ts=1679026485882"]

    def start_requests(self):
        url = "https://www.bingoal.nl/generated/sportHome_uof_4_1.json"
        payload = "func=sportHome&ts=20230323%2010%3A11%3A13&k=5786"
        headers = {
          'authority': 'resources.bingoal.be',
          'accept': '*/*',
          'accept-language': 'en-IN,en-US;q=0.9,en;q=0.8,gu;q=0.7',
          'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'dnt': '1',
          'origin': 'https://www.bingoal.be',
          'referer': 'https://www.bingoal.be/',
          'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
          'sec-ch-ua-mobile': '?0',
          'sec-ch-ua-platform': '"macOS"',
          'sec-fetch-dest': 'empty',
          'sec-fetch-mode': 'cors',
          'sec-fetch-site': 'same-site',
          'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
          'x-requested-with': 'XMLHttpRequest'
        }
        yield scrapy.Request(url=url,headers=headers,body=payload,callback=self.parse)

    def parse(self,response):
        data = json.loads(response.text)
        total_sports = data['today']

        for sport in total_sports:
            sport_name = sport['sport']
            if sport_name.lower() == "cycling":
                continue
            else:
                matches = sport['matches']
                for match in matches:
                    fulltitle = match.get('fullTitle')
                    team1 = fulltitle.split('-')[0]
                    team2 = match.get('team2')
                    date = match.get('date')
                    url = match.get('url')
                    importantSubbets = match.get('importantSubbets')
                    if importantSubbets:
                        moneyline_odds = []
                        both_score_odds = []
                        double_chance_odds=[]
                        handicap_odds = []
                        total_odds = []
                        dnb_odds = []

                        for subset in importantSubbets:
                            bet_type = subset.get('name')
                            odd = subset.get('tips')      
                            odds_count = len(odd)

                            if 'winnaar' in  (bet_type).lower():
                                odds_team1 = odd[0]['odd']
                                odds_team2 = odd[1]['odd']
                                last_data = f"{fulltitle} {team1} {odds_team1}\n{fulltitle} {team2} {odds_team2}"
                                moneyline_odds.append(last_data)

                            elif '1X2' in bet_type:
                                odds_team1 = odd[0]['odd']
                                odds_X = odd[1]['odd']
                                odds_team2 = odd[2]['odd']
                                last_data = f"{fulltitle} {team1} {odds_team1}\n{odds_X}\n{fulltitle} {team2} {odds_team2}"
                                both_score_odds.append(last_data)

                            elif 'dubbele kans' in bet_type.lower():
                                odds_team1X = odd[0]['odd']
                                odds_team12 = odd[1]['odd']
                                odds_teamX2 = odd[2]['odd']
                                last_data = f"{fulltitle};{odds_team1X}\n{fulltitle};{odds_team12}\n{fulltitle};{odds_teamX2}"
                                double_chance_odds.append(last_data)

                            elif 'handicap' in bet_type.lower():
                                    if odds_count == 2:
                                        sov_team1 = odd[0]['sov']
                                        sov_team2 = odd[1]['sov']
                                        odds_team1 = odd[0]['odd']
                                        odds_team2 = odd[1]['odd']
                                        last_data = f"{fulltitle}{team1}{sov_team1}\n{odds_team1}\n{odds_team2} |"
                                        handicap_odds.append(last_data)
                                    else: 
                                        # because Handicap with 3 data we did not have to consider
                                        pass
                            elif 'draw no bet' in bet_type.lower():
                                odds_team1 = odd[0]['odd']
                                odds_team2 = odd[1]['odd']   
                                last_data = f"{fulltitle}{team1}{odds_team1} \n {fulltitle}{team2}{odds_team2}"
                                dnb_odds.append(last_data)

                            elif ('doelpunten'  in bet_type.lower()) or ('totaal aantal punten' in bet_type.lower()):
                                if  odds_count == 2:
                                    o_sov = odd[0]['sov']
                                    odd_over = odd[0]['odd']
                                    odd_under = odd[1]['odd']
                                    last_data = f"{fulltitle}{o_sov}\n{odd_over}\n{odd_under}"
                                    total_odds.append(last_data)
                                elif  odds_count == 4:
                                    o_sov1 = odd[0]['sov']
                                    odd_over1 = odd[0]['odd']
                                    odd_under1 = odd[1]['odd']
                                    o_sov2 = odd[2]['sov']
                                    odd_over2 = odd[2]['odd']
                                    odd_under2 = odd[3]['odd']
                                    last_data = f"{fulltitle}{o_sov1}\n{odd_over1}\n{odd_under1} | {fulltitle}{o_sov2}\n{odd_over2}\n{odd_under2} "
                                    total_odds.append(last_data)
                                elif odds_count == 6:
                                    o_sov1 = odd[0]['sov']
                                    odd_over1 = odd[0]['odd']
                                    odd_under1 = odd[1]['odd']
                                    o_sov2 = odd[2]['sov']
                                    odd_over2 = odd[2]['odd']
                                    odd_under2 = odd[3]['odd']
                                    o_sov3 = odd[4]['sov']
                                    odd_over3 = odd[4]['odd']
                                    odd_under3 = odd[5]['odd']
                                    last_data = f"{fulltitle}{o_sov1}\n{odd_over1}\n{odd_under1} | {fulltitle}{o_sov2}\n{odd_over2}\n{odd_under2} | {fulltitle}{o_sov3}\n{odd_over3}\n{odd_under3}" 
                                    total_odds.append(last_data) 
                            else:
                                pass     

                            yield {
                                    'sport_name':sport_name,
                                    'team_names':fulltitle,
                                    'date':date,
                                    'moneyline_odds':',\n'.join(moneyline_odds),
                                    "both_score_odds":'\n'.join(both_score_odds),
                                    "double_chance_odds":'\n'.join(double_chance_odds),
                                    "handicap_odds":'\n'.join(handicap_odds),
                                    "dnb_odds":'\n'.join(dnb_odds),
                                    "total_odds":'\n'.join(total_odds),
                                    
                                    }    
                    



            










        #  previous api data 

        # for i in data['sports']:
        #     sports_name = i['name']
        #     regions = i['regions']
        #     # one sports all odds add into this list
        #     # data = []
        #     for region in regions:
        #         id = region['ID']       
        #         name = region['name']
        #         divisions = region['divisions']
        #         # if sports_name == "CYCLING":
        #             #     break
        #         # else:

        #         for division in divisions:       
        #             div_id = division['ID']
        #             div_name = division['name']
        #             matches = division['matches']

        #             # one division all odds in this list 
        #             # data = []
        #             for match in matches:
        #                 fulltitle = match['fullTitle']
        #                 team1 = match.get('team1').get('name')                    
        #                 team2 = match.get('team2').get('name')                    
        #                 date = match['date']
        #                 odds = match.get('importantSubbets')

        #                 #  according match type
                        
        #                 moneyline_odds = []
        #                 both_score_odds = []
        #                 double_chance_odds = []
        #                 handicap_odds = []
        #                 dnb_odds = []
        #                 total_odds = []
        #                 if odds:
        #                     for odd in odds:
        #                         # data = []
        #                         bet_type = odd['name']
                                
        #                         odds_count = len(odd['tips'])

        #                         if 'winnaar' in  (bet_type).lower():
        #                             odds_team1 = odd['tips'][0]['odd']
        #                             odds_team2 = odd['tips'][1]['odd']
        #                             numerical = f"{odds_team1}\n{odds_team2}"
        #                             last_data = f"{fulltitle} {team1} {odds_team1}\n{fulltitle} {team2} {odds_team2}"
        #                             moneyline_odds.append(last_data)
        #                             # print("odd_count2:",final_data)

        #                         elif '1X2' in bet_type:
        #                             odds_team1 = odd['tips'][0]['odd']
        #                             odds_X = odd['tips'][1]['odd']
        #                             odds_team2 = odd['tips'][2]['odd']
        #                             numerical = f"{odds_team1}\n{odds_X}\n{odds_team2}"
        #                             last_data = f"{fulltitle} {team1} {odds_team1}\n{odds_X}\n{fulltitle} {team2} {odds_team2}"
        #                             both_score_odds.append(last_data)
        #                             # print("odd_count3:",final_data)

        #                         elif 'dubbele kans' in bet_type.lower():
        #                             odds_team1X = odd['tips'][0]['odd']
        #                             odds_team12 = odd['tips'][1]['odd']
        #                             odds_teamX2 = odd['tips'][2]['odd']
        #                             last_data = f"{fulltitle};{odds_team1X}\n{fulltitle};{odds_team12}\n{fulltitle};{odds_teamX2}"
        #                             double_chance_odds.append(last_data)

        #                         elif 'handicap' in bet_type.lower():
        #                                 if odds_count == 2:
        #                                     sov_team1 = odd['tips'][0]['sov']
        #                                     sov_team2 = odd['tips'][1]['sov']
        #                                     odds_team1 = odd['tips'][0]['odd']
        #                                     odds_team2 = odd['tips'][1]['odd']
        #                                     last_data = f"{fulltitle}{team1}{sov_team1}\n{odds_team1}\n{odds_team2} |"
        #                                     handicap_odds.append(last_data)

        #                                 else: 
        #                                     # because Handicap with 3 data we did not have to consider
        #                                     pass  

        #                         elif 'draw no bet' in bet_type.lower():
        #                             odds_team1 = odd['tips'][0]['odd']
        #                             odds_team2 = odd['tips'][1]['odd']   
        #                             last_data = f"{fulltitle}{team1}{odds_team1} \n {fulltitle}{team2}{odds_team2}"
        #                             dnb_odds.append(last_data)

        #                         elif ('doelpunten'  in bet_type.lower()) or ('totaal aantal punten' in bet_type.lower()):
        #                             if  odds_count == 2:
        #                                 o_sov = odd['tips'][0]['sov']
        #                                 odd_over = odd['tips'][0]['odd']
        #                                 odd_under = odd['tips'][1]['odd']
        #                                 last_data = f"{fulltitle}{o_sov}\n{odd_over}\n{odd_under}"
        #                                 total_odds.append(last_data)
        #                             elif  odds_count == 4:
        #                                 o_sov1 = odd['tips'][0]['sov']
        #                                 odd_over1 = odd['tips'][0]['odd']
        #                                 odd_under1 = odd['tips'][1]['odd']
        #                                 o_sov2 = odd['tips'][2]['sov']
        #                                 odd_over2 = odd['tips'][2]['odd']
        #                                 odd_under2 = odd['tips'][3]['odd']
        #                                 last_data = f"{fulltitle}{o_sov1}\n{odd_over1}\n{odd_under1} | {fulltitle}{o_sov2}\n{odd_over2}\n{odd_under2} "
        #                                 total_odds.append(last_data)
        #                             elif odds_count == 6:
        #                                 o_sov1 = odd['tips'][0]['sov']
        #                                 odd_over1 = odd['tips'][0]['odd']
        #                                 odd_under1 = odd['tips'][1]['odd']
        #                                 o_sov2 = odd['tips'][2]['sov']
        #                                 odd_over2 = odd['tips'][2]['odd']
        #                                 odd_under2 = odd['tips'][3]['odd']
        #                                 o_sov3 = odd['tips'][4]['sov']
        #                                 odd_over3 = odd['tips'][4]['odd']
        #                                 odd_under3 = odd['tips'][5]['odd']
        #                                 last_data = f"{fulltitle}{o_sov1}\n{odd_over1}\n{odd_under1} | {fulltitle}{o_sov2}\n{odd_over2}\n{odd_under2} | {fulltitle}{o_sov3}\n{odd_over3}\n{odd_under3}" 
        #                                 total_odds.append(last_data) 
        #                             else:
        #                                 pass     
        #                         else:
        #                             pass                     
                                        
        #                         # print(sports_name)
        #                         # print(bet_type)                
        #                         # print(data)
                                

        #                 #  for every bet_types 
                        
        #                 yield {
        #                     'sports_name':sports_name,
        #                     # 'region_id':id,
        #                     # 'region_name':name,
        #                     # 'division_id':div_id,
        #                     # 'division_name':div_name,
        #                     'team_names':fulltitle,
        #                     # 'team1':team1,
        #                     # 'team2':team2,
        #                     'date':date,
        #                     'moneyline_odds':',\n'.join(moneyline_odds),
        #                     "both_score_odds":'\n'.join(both_score_odds),
        #                     "double_chance_odds":'\n'.join(double_chance_odds),
        #                     "handicap_odds":'\n'.join(handicap_odds),
        #                     "dnb_odds":'\n'.join(dnb_odds),
        #                     "total_odds":'\n'.join(total_odds)
                            
        #                     }    

                    # for every match     
                    # print(sports_name)
                    # print(bet_type)
                    # print(data)   

            # first data[]
            # print(sports_name)                
            # print(data)    








                            # odds = []
                            # for s_odd in odd['tips']:
                            #     s_odd['odd']
                            
                        # odds_team1 = odds[0]['tips'][0]['odd']
                        # odds_X = odds[0]['tips'][1]['odd']
                        # odds_team2 = odds[0]['tips'][2]['odd']
                        
                    # else:
                    #    odds_team1 = 0
                    #    odds_team2 = 0
                    
                
                    # yield {
                    #     'sports_name':sports_name,
                        #     'region_id':id,
                        #     'region_name':name,
                        #     'division_id':div_id,
                        #     'division_name':div_name,
                        #     'fulltitle':fulltitle,
                        #     'team1':team1,
                        #     'team2':team2,
                        #     'date':date,
                        #     'odds_team1':odds_team1,
                        #     'odds_team2':odds_team2
                        # }