import requests
import time
import heapq


URL_TYPE = ["oas", "wav", "ids", "vul", "mav", "ods"]
ATTACK_TYPE = ["Total", "Dos", "Backdoor", "Trojan", "DangerousObject", "Exploit",\
               "HackTool", "Bruteforce", "Scan", "Network", "Spam", "Other"]


country_id_dict = {"Russia": 213, "China": 137}#, "Japan": 45, "South Korea": 37, \
#                "India": 159,"United Arab Emirates": 192, "Saudi Arabia": 219,\
#                "Thiland": 33,"Singapore": 214,"Vietram": 50,"Philippines": 154,\
#                "Spain": 46,"Italy": 125,"France": 177,"Ukraine": 27,"Switzerland": 48,\
#                "Turkey": 197,"Germany": 81,"Belgiam": 29,"Netherlands": 1,\
#                "United Stated": 109,"Canada": 109,"Mexcia": 72,"Bolivia": 6,\
#                "Brazil": 215,"Chile": 100,"Colombia": 152,"Ecuadaor": 35,"Peru": 4,\
#                "Egypt": 5,"Nigeria": 141 ,"Algeria": 129,"Sudan": 198,"Libya": 220,\
#                "South Africa": 74,"Morocco": 24, "New Zealand": 127 ,"Australia": 176}

potential_country = [x for x in country_id_dict]

country_data_dict = dict()


index_of_attack_by_country=10



def create_each_country():
    each_country = dict()
    for item in ATTACK_TYPE:
        each_country[item] = 0
    
    each_country["Rank"] = list()
    
    return each_country

    

def total_attack_per_type_per_period(total_url):
    res = requests.get(total_url)
    
    date_count_list = res.text.split(', ')

    total = 0
    for line in range(0, len(date_count_list), 2):
        
        cnt = date_count_list[line].split()[1]
        total = total + float(cnt)
    return total


def add_attack_data(attack_url, each_country, total_attack):
    res = requests.get(attack_url)
    two_cnt = 0
    
    top_ten = res.text.split(", ")
    
    for line in range(0, len(top_ten)):
        
        if(line % 2 == 0):
            pos = top_ten[line].find(" ")
            percent = float(top_ten[line][pos:])
            two_cnt = two_cnt + 1
        else:
            pos = top_ten[line].find(': "')
            first_dot = top_ten[line].find(".")
            
            attack = top_ten[line][pos+3 : first_dot]
            two_cnt = two_cnt + 1
        
        if(two_cnt == 2):
            try:
                each_country[attack] = each_country[attack] + total_attack * 0.01 * percent
                
            except:
                each_country["Other"] = each_country["Other"] + total_attack * 0.01 * percent
            
            two_cnt = 0

def attack_type_percentage_per_period(each_country, country_id):
    
    
    for atktype in URL_TYPE:
        
#==============================================================================
        total_url =  'https://cybermap.kaspersky.com/data/securelist/graph_' + atktype + '_m_' + str(country_id) + '.json'
        attack_url = 'https://cybermap.kaspersky.com/data/securelist/top10_' + atktype + '_m_' + str(country_id) + '.json'
        
        total_attack = total_attack_per_type_per_period(total_url)
        each_country["Total"] = each_country["Total"] + total_attack
        
        
        add_attack_data(attack_url, each_country, total_attack)
        
#==============================================================================

        
#==============================================================================
#SPAM
    spam_total_url = 'https://cybermap.kaspersky.com/data/securelist/graph_kas_m_' + str(country_id) + '.json'

    spam_url = 'https://cybermap.kaspersky.com/data/securelist/top10_kas_m_' + str(country_id) + '.json'
    
    total_attack = total_attack_per_type_per_period(spam_total_url)
    each_country["Total"] = each_country["Total"] + total_attack
    
    res = requests.get(spam_url)
    
    spam_list = res.text.split(", {")
    
    
    for line in spam_list:
        first_space = line.find(" ")
        comma_pos = line.find(",")
        
        
        percent = float(line[first_space+1 : comma_pos])


        each_country["Spam"] = each_country["Spam"] + total_attack * 0.01 * percent
#==============================================================================

def add_rank(country_dict):
    
    temp_list = list()
    max_list = list()
    reverse_dict = dict()
    
    for item in ATTACK_TYPE:
        temp_list.append(country_dict[item])
        reverse_dict[country_dict[item]] = item
        
    max_list = heapq.nlargest(6, temp_list)
    for item in max_list:
        country_dict["Rank"].append(reverse_dict[item])
    
    country_dict["Rank"].pop(0)
    
#    print(country_dict["Rank"])



def write_in_total(country_data_dict):
    out_file = open("total.txt", "w")
    
    for country in country_data_dict:
#        print()
#        print(country)
        out_file.write("{}\n".format(country))
        
#        for cnt in range(0, len(country_data_dict[country])-1):
#            out_file.write("{:15s}  {:>15,.0f}\n".format(item, country_data_dict[country][cnt]))
        
        for item in country_data_dict[country]:
#            print("{:15s}  {:>15,.0f}".format(item, country_data_dict[country][item]), out_file)
            
            if(item == "Rank"):
                break
            
            out_file.write("{:15s}  {:>15,.0f}\n".format(item, country_data_dict[country][item]))
        out_file.write("\n")
    out_file.close()


def write_sep(country_data_dict):
    
    for country in country_data_dict:
        
        out_file = open("sep\\" + country + ".txt", "w")
        
        out_file.write("{}\n\n".format(country))
        out_file.write("Rank    Type                Count        (%)\n")
#        out_file.write("{:^8s}{:15s}{:^15s}\n".format("Rank", "Type", "Count"))
        
        for rank in range(0,5):
            
            Type = country_data_dict[country]["Rank"][rank] #"Dos",...
            count = country_data_dict[country][Type]
            
            perc = count / country_data_dict[country]["Total"] * 100
#            print(country_data_dict[country]["Total"])
            out_file.write("{:^3d}    {:15s} {:>13,.0f}   {:5.2f}\n".format(rank+1, Type, count, perc))
            
#            print("{:15s}  {:>15,.0f}".format(item, country_data_dict[country][item]), out_file)
            
#            out_file.write("{:15s}  {:>15,.0f}\n".format(item, country_data_dict[country][item]))

        out_file.close()


def write_html(country_data_dict):
    
    for country in country_data_dict:
        out_file = open("html\\" + country + ".html", "w")

        out_file.write('<!DOCTYPE html>\n<html>\n  <head>\n    <meta charset="utf-8">\n    <link href="https://fonts.googleapis.com/css?family=Audiowide" rel="stylesheet">\n    <title>')

        out_file.write('country')
        out_file.write('</title>\n    <style>\n    .topleft {\n    position: absolute;\n    top: 105px;\n    left: 140px;\n}\n  h1{\n      text-align:center;\n      font-family: "Audiowide", cursive;\n      color:#FFFFFF;\n      font-size: 100px;\n      padding:5px\n    }\n')
        out_file.write('  table {\n    font-family: arial, sans-serifs;\n    border-collapse: collapse; width: 80%;\n    height: 50%;\n    padding: 20px;\n    text-align: center;\n  }\n\n')
        out_file.write('  td,th {\n\n    border: 5px solid #000000;\n    text-align: center;\n    padding: 20px;\n  }\n\n')
        out_file.write('  tr:nth-child(odd) {\n    background-color: #FFFFFF;\n  }\n  tr:nth-child(even) {\n    background-color: #C0C0C0;\n  }\n')
        out_file.write('  </style>\n  </head>\n  <body bgcolor="#000000">\n    <h1>')
        out_file.write('{}'.format(country))
        out_file.write('</h1>\n    <a href="***">\n  <img class="topleft" src="arrow.png" alt="arrow" style="width:60px;height:60px;border:0;">\n')
        out_file.write('</a>\n    <table align = "center">\n  <tr>\n    <th>Rank</th>\n    <th>Type</th>\n    <th>Count</th>\n    <th>Percentage %</th>\n  </tr>\n')
        
        for rank in range(0,5):
            Type = country_data_dict[country]["Rank"][rank] #"Dos",...
            count = country_data_dict[country][Type]
            perc = count / country_data_dict[country]["Total"] * 100
           
            out_file.write('  <tr>\n    <td>')
            out_file.write('{:d}'.format(rank+1))
            out_file.write('</td>\n    <td>')
            out_file.write('{:s}'.format(Type))
            out_file.write('</td>\n    <td>')
            out_file.write('{:,.0f}'.format(count))
            out_file.write('</td>\n    <td>')
            out_file.write('{:.2f}'.format(perc))
            out_file.write('</td>\n  </tr>\n')
            
        out_file.write('  </table>\n  </body>\n</html>\n')
    
    out_file.close()


def read_all():
    for country in potential_country:
        country_data_dict[country] = create_each_country()
    
        attack_type_percentage_per_period(country_data_dict[country], country_id_dict[country])


        # add to rank
        add_rank(country_data_dict[country])

    return country_data_dict



def main():
    
    start_time = time.time()
    
    country_data_dict = read_all()
    
    
    
    
    
    
        
        

#    write_sep(country_data_dict)
    
#    write_html(country_data_dict)
    write_in_total(country_data_dict)

    end_time = time.time()
    
    print()
    print(len(country_data_dict), "Countries Cost", end_time - start_time, "seconds")
    
    
if __name__ == "__main__":
    main()

    
    