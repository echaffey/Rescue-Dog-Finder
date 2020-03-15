from bs4 import BeautifulSoup
import urllib.request
import pickle
from emailer import Message
from jinja2 import Template

URL = 'http://api.petfinder.com/shelter.getPets?key=106967c5aea8aaac1356a884a5eae24c&id=LA366'
source = urllib.request.urlopen(URL).read()
soup = BeautifulSoup(source, 'xml')
msg = Message()

def parse_file():
    with open('dogNames.pkl', 'rb+') as f:
        try:
            pickle_file_data = pickle.load(f)
        except EOFError:
            pickle_file_data = []
    return pickle_file_data

def dog_seen(dog_to_check_for, list_to_check):
    for dict_item in list_to_check:
        if dict_item['name'] == dog_to_check_for:
            return True
    return False

def build_HTML_file(dogs_to_email):
    html = '''
        <html>
            <body>
                <p><b><u>NEW DOGGOS:</u></b></p></br>
                {% for dog in dogs_to_email %}
                    <a href="http://www.cenlaallianceforanimals.com/Adopt/ViewAnimal?petId={{ dog['ID'] }}">
                    {{ dog['name'] }} [{{ dog['sex'] }}] {{ dog['breed'] }} Size: {{ dog['size'] }}
                    </a>
                    </br>
                    </br>
                {% endfor %}
            </body>
        </html>
    '''
    template = Template(html)
    print(template)
    return template.render(dogs_to_email=dogs_to_email)

def collect_dogs():
    dogs_already_seen = parse_file()
    pet_list = []

    for pets in soup.find_all('pet'):
        if dog_seen(pets.find('shelterPetId').text, dogs_already_seen) is not True:
            pet = {}
            pet['name'] = pets.find('shelterPetId').text
            pet['ID'] = pets.find('id').text
            pet['breed'] = pets.find('breed').text
            pet['sex'] = pets.find('sex').text
            pet['size'] = pets.find('size').text
            pet['photo'] = pets.find_all('photo')[0].text
            pet_list.append(pet)

    if len(pet_list)>0:        
        msg_html = build_HTML_file(pet_list)
        msg.send_email(msg_html)
        update_file(pet_list)

def update_file(dict_to_write):
    file_data = []
    with open('dogNames.pkl', 'rb+') as f:
        try:
            file_data = pickle.load(f)
        except EOFError:
            file_data = []

    with open('dogNames.pkl', 'wb+') as f:
        pickle.dump(file_data + dict_to_write, f)

if __name__ == '__main__':
    collect_dogs()
