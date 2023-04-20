import win32com.client
import pandas as pd
import re



class parser:
    def __init__():
        pass
    def folder_parse (act_folder):
        folder_list = [act_folder]
        for folder in act_folder.Folders:
            if len(folder.Folders) == 0:
                folder_list.append(folder)
            elif len(folder.Folders) > 0:
                folder_list.extend(parser.folder_parse(folder))
        return(folder_list)
    def message_parse (folder_list):
        message_list = []
        for folder in folder_list:
            #print(folder.name)
            if len(folder.Items)>0:
                folder_messages = [item for item in folder.Items if hasattr(item,"To")]
                #print(len(folder_messages))
                message_list.extend(folder_messages)
        return(message_list)

class email_leads:
    def __init__(self):
        self.outlook = win32com.client.Dispatch('outlook.application')
        self.mapi = self.outlook.GetNamespace('MAPI')
        self.leadsfile = pd.read_excel('his_autoleads.xlsx', sheet_name = 'leads')
        self.blacklist = pd.read_excel('his_autoleads.xlsx', sheet_name = 'blacklist')
        self.notes = pd.read_excel('his_autoleads.xlsx', sheet_name = 'notes')
        self.greetinglist = ["Dear", "Hi", "Hej"]
        self.outboundlist = [
            "admission@his.se", 
            "antagning@his.se",
            "study@his.se", 
            "international@his.se", 
            "/o=HS/ou=Exchange Administrative Group (FYDIBOHF23SPDLT)/cn=Recipients/cn=ERK Internationella relationer",
            "/O=HS/OU=EXCHANGE ADMINISTRATIVE GROUP (FYDIBOHF23SPDLT)/CN=RECIPIENTS/CN=GROUPFBED2757",
            "/O=HS/OU=EXCHANGE ADMINISTRATIVE GROUP (FYDIBOHF23SPDLT)/CN=RECIPIENTS/CN=FFCD4C9EEF41453FACB92E986161060B-INTERNATIONAL"]
        self.lead_diclist = []
    def folderscraper(self, accounts = ['University of Skövde - Study', 'University of Skövde - International Office'], main = "Archive"):
        self.folders = sum([parser.folder_parse(self.mapi.Folders[account].Folders[main].Folders['Prospective Students']) for account in accounts],[])
    def messagescraper(self):
        self.messages = parser.message_parse(self.folders)
    def get_non_HiS (self, message):
        email_pattern = r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)'
        email_list = re.findall(email_pattern, message.Body)
        non_his_se_emails = [email for email in email_list if not email.endswith('his.se')]
        return(non_his_se_emails)
    def remove_duplicates(self, lst):
        lst = sorted(lst, key=lambda k: k['time_added'])
        unique_emails = set()
        new_lst = []
        for d in lst:
            email = d['email']
            if email not in unique_emails:
                unique_emails.add(email)
                new_lst.append(d)
        return new_lst

    def extract_leads(self):
        direct = self.remove_duplicates([{
            "name" : message.Sender.Name if "@" not in message.Sender.Name else "Unknown",
            "email" : message.Sender.Address,
            "time_added" : message.Creationtime.strftime("%Y-%m-%d %H:%M:%S")
        }
            for message in self.messages if "@" in message.Sender.Address and not message.Sender.Address.endswith('his.se')])
        redirected = list(set(sum([self.get_non_HiS(message) for message in self.messages if "@" not in message.Sender.Address],[])))
        result = direct
        for email in redirected:
            result.append({"name" : "Unknown", "email":email})
        return(result)
        
    def check_blacklist(self, lead:dict):
        email = lead['email'].lower()
        name = lead['name'].lower()
        domain = email.split('@')[1]
        if email in self.blacklist['Email'].str.lower().values:
            return True
        if name in self.blacklist['Name'].str.lower().values:
            return True
        if domain in self.blacklist['Domain'].str.lower().values:
            return True
        return False
    def leadfile_blacklistcheck(self):
        self.leadsfile = pd.DataFrame([lead for lead in self.leadsfile.to_dict(orient='records') if not self.check_blacklist(lead)])
    def write_out(self, filepath: str = "his_autoleads"):
        filtered_leads = pd.DataFrame([lead for lead in self.extract_leads() if not self.check_blacklist(lead)])
        new_leads = filtered_leads[~filtered_leads['email'].isin(self.leadsfile['email'])]
        df = pd.concat([self.leadsfile, new_leads], ignore_index=True)
        df = df.sort_values(by="time_added", ascending=False).drop_duplicates(subset='email', keep="first")
        try:
            # Write the dataframe to an excel file
            with pd.ExcelWriter(filepath + '.xlsx') as writer:
                df.to_excel(writer, sheet_name="leads", index=False)
                self.blacklist.to_excel(writer, sheet_name="blacklist", index=False)
                self.notes.to_excel(writer, sheet_name="notes", index=False)
            print('Dataframe successfully written to excel file.')
            
        except Exception as e:
            print('Error writing dataframe to excel file:', e)
    

def new_main():
    emails = email_leads()
    emails.folderscraper()
    emails.messagescraper()
    emails.leadfile_blacklistcheck()
    emails.write_out()
    input("Process done")
new_main()