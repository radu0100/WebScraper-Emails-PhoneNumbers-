import csv
import urllib.request                                                                     #imported required libraries
import re
from socket import timeout


def read_from_csv(websites_csv_path):
    list = []
    with open(websites_csv_path, 'r') as file:                                            #createad a function to read all the websites from the csv file
        csvreader = csv.reader(file)
        for row in csvreader:
            list.append(row.pop())
    return list


def add_required_header(websites):
    for i in range(0, len(websites)):                                                     #I've noticed that all the websites inside the csv file did not have a
        websites[i] = 'https://www.' + websites[i]                                        # 'https://www.' at the beginning so i createad a header to easily access them.


def find_mail_in_website(a_website):
    try:                                                                                  #Based on a function found online i managed to read all the strings present
        match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', a_website.decode("utf-8"))         #on each website that had the following format a combination of words and
        if match is not None:                                                             #symbols followed by '@' followed by another string followed by a '.' and another
            return match.group(0)                                                         #word.
    except timeout and Exception:                                                         #If the scraper could not find any string in this format on the website,
        return None                                                                       #it would ignore it and move to the next one.


def find_phone_number_in_website(phone):
    try:
        decodedPhone = phone.decode("utf-8")
        decodedPhone.replace(' ', '')                                                     #I removed all the spaces from the websited so the phone number could be read easier
        match2 = decodedPhone.split(">+")[1].split("<")[0]                                #I looked for all the phone number format that would start with a + and end with a number(also removed thye '+' sign so i can see only the numbers
        phoneNR = "+" + match2                                                            #Added back the removed '+' so the scraper could return an actual phone number format.
        return phoneNR
    except timeout and Exception:                                                         #Same as mails, any website that would return a timeout or an exception(Access forbidden/denied) would be ignored.
        return None


def exclude_invalid_websites(website):
    try:
        return urllib.request.urlopen(website, timeout=0.5).read()                        #If a website would take to lokg to return the request it would be ignored and move on to the next.
    except timeout and Exception:
        return None


def get_mails_from_websites(websites):
    mails = {}
    for website in websites:
        mails[website] = ''
        response = exclude_invalid_websites(website)                                     #This fuction recovers all the emails found on the main page of each website
        if response is not None:
            mail = find_mail_in_website(response)
            if mail is not None:
                mails[website] = mail + ''
    return mails


def get_phone_number_from_website(websites):
    phone_numbers = {}
    for website_PH in websites:
        phone_numbers[website_PH] = ''
        response = exclude_invalid_websites(website_PH)                                 #This fuction recovers all the phone numbers found on the main page of each website
        if response is not None:
            phone_number = find_phone_number_in_website(response)
            if phone_number is not None:
                phone_numbers[website_PH] = phone_number + ''
    return phone_numbers


def write_file(websites_and_emails, mails_and_websites_map):
    with open(websites_and_emails, 'w') as file:
        csvwrite = csv.writer(file)                                                    #This function will write all the websites and emails in a csv file
        for key in mails_and_websites_map.keys():                                      #Note: some websites don't have the email adress on the main page of the website
            csvwrite.writerow([key + " - " + mails_and_websites_map.get(key)])         #due to this, the scraper won't return any result for some wesites.


def merge_dicts(dict1, dict2):
    for key in dict1.keys():                                                          #Merge function to combine the mail adresses and phone numbers in a single CSV file.
        dict1[key] = dict1.get(key) + " - " + dict2.get(key)
    return dict1


if __name__ == '__main__':
    websites = read_from_csv('./sample-websites.csv')                                #reading the csv file

    websites.pop(0)                                                                  #ignoring the first line in the csv since it's not a website link but a collumn name

    add_required_header(websites)                                                    #adding the required header so the scaper can easily access all the websites

    print(websites)                                                                  #print all the websites found in the csv file

    mails_and_websites_map = get_mails_from_websites(websites)                       #identifing and reading all the emails from each website(if possible)
    print(mails_and_websites_map)

    PH_and_website_map = get_phone_number_from_website(websites)                     #identifing and reading all the phone numbers from each website(if possible)
    print(PH_and_website_map)

    final_map = merge_dicts(mails_and_websites_map, PH_and_website_map)              #merging all emails and phone numbers in one csv file
    write_file('./Emails&PhoneNumbers.csv', final_map)
