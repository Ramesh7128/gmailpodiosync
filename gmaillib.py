import atom.data
import gdata.data
import gdata.contacts.client
import gdata.contacts.data
import requests
import json
import time
client_id='employees-lurbta'
client_secret= 'jgc4jqCoOZYjR7MCw6mJYliMdoNMrKF8pQaoQ9AbXhoXy3IT45ptTDPBQ83Safu9'
refresh_token= 'fe99b1497eb54bf785b4640b526bf988'
app_id = 10740730
accesstoken = "855fc0e2fb164cdca2d0da2184a1fc1b"

client = gdata.contacts.client.ContactsClient(source='podiosync')
client.ClientLogin('rameshravi7128@gmail.com', 'findout7128', client.source);

group_name = {'Employee':'Employees working for startups from jaaga penthouse', 'Founder':'startups founder', 'Jaaga':'others', 'others': 'just others'}
group_status = []

######################### google ######################################

def PrintAllContacts(gd_client):
  feed = gd_client.GetContacts()
  for i, entry in enumerate(feed.entry):
    print entry.name
    #print '\n%s %s' % (i+1, entry.name.full_name.text)
    if entry.content:
      print '    %s' % (entry.content.text)
    # Display the primary email address for the contact.
    for email in entry.email:
      if email.primary and email.primary == 'true':
        print '    %s' % (email.address)
    # Show the contact groups that this contact is a member of.
    for group in entry.group_membership_info:
      print '    Member of group: %s' % (group.href)
    # Display extended properties.
    for extended_property in entry.extended_property:
      if extended_property.value:
        value = extended_property.value
      else:
        value = extended_property.GetXmlBlob()
      print '    Extended Property - %s: %s' % (extended_property.name, value)


def PrintAllGroups(gd_client, status=""):
  feed = gd_client.GetGroups()
  for entry in feed.entry:
    if entry.title.text == status:
      return entry.id.text
    print 'Atom Id: %s' % entry.id.text
    print 'Group Name: %s' % entry.title.text
    print 'Last Updated: %s' % entry.updated.text

    print 'Extended Properties:'
    for extended_property in entry.extended_property:
      if extended_property.value:
        value = extended_property.value
      else:
        value = extended_property.GetXmlBlob()
      print '  %s = %s' % (extended_property.name, value)
    print 'Self Link: %s' % entry.GetSelfLink().href
    if not entry.system_group:
      print 'Edit Link: %s' % entry.GetEditLink().href
      print 'ETag: %s' % entry.etag
      print
      print
    else:
      print 'System Group Id: %s' % entry.system_group.id
      print
      print

def delete_groups_of_podio(gd_client):
  feed = gd_client.GetGroups()
  for entry in feed.entry:
    if entry.title.text in group_status:
      print entry.title.text
      print entry.GetSelfLink().href
      delete_contact_group(gd_client, entry.GetSelfLink().href)

def delete_contact_group(gd_client, contact_group_url):
  # Retrieving the contact group is required in order to get the Etag.
  group = gd_client.GetGroup(contact_group_url)
  print group
  try:
    gd_client.Delete(group)
  except gdata.client.RequestError, e:
    if e.status == 412:
      # Etags mismatch: handle the exception.
      pass
                              
def create_contact_group(gd_client):
  #for key, value in group_name.items():
  for key in group_status:
    new_group = gdata.contacts.data.GroupEntry(title=atom.data.Title(text=key))
    #new_group.extended_property.append(
        #gdata.data.ExtendedProperty(name='more info about the group', value=value))

    created_group = gd_client.CreateGroup(new_group)
    print "Contact group's Atom Id: %s" % created_group.id.text


def create_podio_contacts():
    res = podiocontactsfetch(accesstoken)
    name=""
    primary_email=""
    phone_no=""
    status = ""
    if 'error' in res.keys():
        print "access token expired"
        access_token = refreshpodioaccesstoken()
        res = podiocontactsfetch(access_token)

    for key,value in res.items():
        if key=="items":
            for l in value:
                for k, v in l.items():
                    #if k=="title":
                      #name = v
                    if k=="fields":
                        for m in v:
                            for x,y in m.items():
                                if x=="external_id" and y=="full-name-2":
                                    name = m['values'][0]['value']
                                if x=="external_id" and y=="email-address":
                                    primary_email =  m['values'][0]['value']
                                if x=="external_id" and y=="phone-number-2":
                                    phone_no = m['values'][0]['value']
                                if x=="external_id" and y=="role":
                                    status =  m['values'][0]['value']['text']
                  
                if name and primary_email:  
                  if phone_no and status:
                    create_contact(client, name, primary_email, phone_no, status)
                  elif phone_no:
                    create_contact(client, name, primary_email, phone_no)
                  elif status:
                    create_contact(client, name, primary_email,status)
                  else:
                    status="others"
                    create_contact(client, name, primary_email,status)
                  name=""
                  primary_email=""
                  phone_no=""
                print "-----------------------------------------------------------------------------------"



def create_contact(gd_client,name, primary_email, phone_no="",status=""):
  #name="Vaibhav"
  notes=""
  #primary_email="ramesh7128@gmail.com"
  group_atom = PrintAllGroups(client,status)
  group_atom_id="http://www.google.com/m8/feeds/groups/rameshravi7128%40gmail.com/base/28c3264309fe5ed0"
  #phone_no="9962478798"
  
  new_contact = gdata.contacts.data.ContactEntry(name=gdata.data.Name(full_name=gdata.data.FullName(text=name)))
  new_contact.content = atom.data.Content(text=notes)
    # Create a work email address for the contact and use as primary. 
  new_contact.email.append(gdata.data.Email(address=primary_email, 
        primary='true', rel=gdata.data.WORK_REL))
  if phone_no:
    new_contact.phone_number.append(gdata.data.PhoneNumber(text=phone_no,
        rel=gdata.data.WORK_REL, primay='true'))
  new_contact.group_membership_info.append(gdata.contacts.data.GroupMembershipInfo(href=group_atom))
  entry = gd_client.CreateContact(new_contact)
  print entry.GetId()


def print_query_results(gd_client, url=""):
  url="http://www.google.com/m8/feeds/groups/rameshravi7128%40gmail.com/base/2bbfed208aff6994"
  query = gdata.contacts.client.ContactsQuery()
  query.max_results = 200
  query.group = url
  feed = gd_client.GetContacts(q = query)
  #print feed
  for contact in feed.entry:
    print contact.id.text
    delete_contact(client, contact.id.text)
    print contact.name.full_name.text
    print 'Updated on %s' % contact.updated.text
    

def delete_contact(gd_client, contact_url):
  # Retrieving the contact is required in order to get the Etag.
  contact = gd_client.GetContact(contact_url)

  try:
    gd_client.Delete(contact)
  except gdata.client.RequestError, e:
    if e.status == 412:
      # Etags mismatch: handle the exception.
      pass

############################# podio #################################

def refreshpodioaccesstoken():
    payload = {'grant_type': 'refresh_token', 'client_id': '%s' % (client_id,), 'client_secret': '%s' % (client_secret,), 'refresh_token': '%s' % (refresh_token,)}
    response = requests.post("https://podio.com/oauth/token", data=payload)
    data = response
    res = data.json()
    print res['access_token']
    return res['access_token']

def podiocontactsfetch(accesstoken):    
    response = requests.get('https://api.podio.com/item/app/%s/?limit=147' % (app_id,), headers={'Authorization': 'OAuth2 %s' % (accesstoken,)})
    data = response
    res = data.json()
    return res
    
def podiocontacts():
    res = podiocontactsfetch(accesstoken)
    if 'error' in res.keys():
        print "access token expired"
        access_token = refreshpodioaccesstoken()
        res = podiocontactsfetch(access_token)

    for key,value in res.items():
        if key=="items":
            for l in value:
                for k, v in l.items():
                    #if k=="title":
                      #  print v
                    if k=="fields":
                        for m in v:
                            for x,y in m.items():
                                if x=="external_id" and y=="full-name-2":
                                    print m['values'][0]['value']
                                if x=="external_id" and y=="email-address":
                                    print m['values'][0]['value']
                                if x=="external_id" and y=="phone-number-2":
                                    print m['values'][0]['value']
                                if x=="external_id" and y=="role":
                                    t = m['values'][0]['value']['text']
                                    print t
                                    if t not in group_status:
                                      group_status.append(t)
                                                                                  
                print "-----------------------------------------------------------------------------------"
    group_status.append("others")

def delete_contacts_from_each_groups():
  for i in group_status:
    url = PrintAllGroups(client, i)
    print_query_results(client,url)
  
    
podiocontacts()
#create_contact_group(client)
#create_podio_contacts()
#delete_groups_of_podio(client)
#PrintAllGroups(client)
#PrintAllContacts(client)
#print_query_results(client) #deletes the contacts in the group individually
#PrintAllGroups(client)
delete_contacts_from_each_groups()


