import requests
import time
import csv

from bs4 import BeautifulSoup

class NHS_Facility:
    def __init__(self, name=None, type=None, street_address=None, postcode=None):
        self.name = name
        self.type = type
        self.street_address = street_address
        self.postcode = postcode

    def set_street_address(self, new_address):
        self.street_address = new_address

        address_split = self.street_address.split(", ")
        self.zipcode = address_split[-1]

    def set_postcode(self, new_postcode):
        self.postcode = new_postcode

    def set_type(self, type):
        self.type = type

    def __str__(self):
        return self.name + " | " + self.street_address + " | " + self.type

def parse_type(class_name):
    if class_name == "uc-service-pharmacy":
        return "Pharmacy"
    elif class_name == "uc-service-ae":
        return "Accident and Emergency (A&E)"
    else:
        return "Urgent Care"

def parse_facility_card(nhs_facility_card):
    # Check if not a tag type for whatever reason
    if nhs_facility_card.name == None: return

    nhs_facility_header = nhs_facility_card.find("div", {"class" : "mapview-details-header"})
    nhs_facility_name = nhs_facility_header.h2.a.get_text()
    nhs_type = parse_type(nhs_facility_header.h2.span.get("class")[0])

    new_facility = NHS_Facility(nhs_facility_name, nhs_type)

    nhs_address_container = nhs_facility_card.find("p", {"class" : "fcaddress"})
    nhs_address_breakdown = nhs_address_container.children
    nhs_combined_address = ""
    is_first = True
    for nhs_address_component in nhs_address_breakdown:
        address_component_trimmed = str(nhs_address_component).strip()
        if "<br" not in address_component_trimmed:
            if not is_first: nhs_combined_address += ", "
            else: is_first = False

            nhs_combined_address += address_component_trimmed
    new_facility.set_street_address(nhs_combined_address)

    return new_facility

time_between_pages = 3
# Use these to change the search parameters
search_distance = '15'
include_ae = 'True'
include_pharmacy = 'False'
include_urgent = 'True'
current_page = 1

all_nhs_facilities = []
while(True):
    nhs_url = "https://www.nhs.uk/service-search/UrgentCare/UrgentCareFinder?Location.Id=0&Location.Name=SE1%208XR&Location.Latitude=51.5048179626465&Location.Longitude=-0.11363697052002&IsAandE=" + include_ae +"&IsPharmacy=" + include_pharmacy + "&IsUrgentCare=" + include_urgent + "&IsOpenNow=False&MileValue=" + search_distance + "&currentPage=" + str(current_page)
    nhs_initial_request = requests.get(nhs_url)
    nhs_web_soup = BeautifulSoup(nhs_initial_request.content, 'html.parser')

    nhs_facility_container = nhs_web_soup.find("div", {"class" : "mapview-details-content"})
    if nhs_facility_container == None:
        print("Reached the end of the list")
        break

    nhs_facility_list = nhs_facility_container.find("ul")
    nhs_facility_cards = nhs_facility_list.children
    for nhs_facility_card in nhs_facility_cards:
        new_facility = parse_facility_card(nhs_facility_card)
        if new_facility == None: continue

        all_nhs_facilities.append(new_facility)

    # sleep for a few seconds before requesting the next page
    current_page+=1
    time.sleep(time_between_pages)
    print("Moving on to page: " + str(current_page))

print("Done printing to csv")
with open("nhs_facilities.csv", mode="w") as csv_file:
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(["Name", "Address", "Zipcode", "Type"])
    for nhs_facility in all_nhs_facilities:
        csv_writer.writerow([nhs_facility.name, nhs_facility.street_address, nhs_facility.zipcode, nhs_facility.type])
