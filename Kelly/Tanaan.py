import data
import datetime

kaikki_ravit = data.listat()
pvm = datetime.datetime.now().strftime('%d.%m.%Y')
for ravit in kaikki_ravit:
    if ravit['date'] == pvm:
        a = ravit.find('pool')['file'].split('_')
        print(ravit['name'], ravit['code'], ravit['track-code'], a[0])
