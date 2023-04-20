import requests
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse


class ActiveDF:
    def __init__(self) -> None:
        try:
            self.LeadDF = pd.read_excel("keystone_output.xlsx")
            self.After = parse(self.LeadDF.added.max()).strftime("%Y-%m-%d %H:%M:%S")
            self.Before = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except IOError:
            self.LeadDF = pd.DataFrame()
            self.After = (datetime.datetime.now() - relativedelta(years=3)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.Before = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print ("Output last updated " + self.After)
    def update(self, load):
        for n in load["data"]:
            condense = pd.DataFrame(
                {
                    "first_name": n["firstname"],
                    "last_name": n["lastname"],
                    "email": n["contact"]["email"],
                    "date_of_birth": n["date_of_birth"],
                    "gender": n["gender"],
                    "phone": n["contact"]["phone"],
                    "country": n["contact"]["country"]["name"],
                    "nationality": n["contact"]["nationality_country"]["country_name"],
                    "highest_degree": n["highest_degree"],
                    "program_interest": n["program"]["name"],
                    "added": n["registered"],
                },
                index=[0],
            )
            self.LeadDF = pd.concat([condense, self.LeadDF], ignore_index=True)
        print("Retrieved back to: " + condense.added.min())
        self.Before = condense.added.min()

    def API_import(self):
        base_url = "https://smarthub.keystoneacademic.com/api/rest/getLead"
        request_headers = {
            "x-api-key": "ENTERAPIKEYHERE",
        }
        data = {"limit": "50", "before": self.Before, "after": self.After}
        #print(data)
        act = requests.post(base_url, data=data, headers=request_headers)
        load = act.json()
        #print(load)
        return load


def autoupdate(obj):
    load = 0
    print("Working...")
    while load != "Complete":
        load = obj.API_import()
        #print(load["data"])
        if load['data']:
            if len(load["data"]) == 50:
                obj.update(load)
                #print("Retrieved back to: " + obj.LeadDF.added.min())
                print("Working on the next bit...")
            else:
                obj.update(load)
                load = "Complete"
                obj.write_sw = True
        else:
            print("No new leads since last run.")
            load = "Complete"
            obj.write_sw = False
    input("Task complete. \nPress enter to continue")


def write_file(obj):
    print("Writing file...")
    df = obj.LeadDF.drop_duplicates(subset=['email'],keep='last').sort_values(by="added", ascending=False)
    df.to_excel(
        "keystone_output.xlsx",
        index=False,
    )
    input("File written. Job Complete. \nPress enter to exit.")


def main():
    Keystone = ActiveDF()
    autoupdate(Keystone)
    if Keystone.write_sw ==True:
        write_file(Keystone)

main()
# Keystone.LeadDF
# Keystone.After
# Keystone.Before

# load1 = Keystone.API_import()
# len(load1["data"])
