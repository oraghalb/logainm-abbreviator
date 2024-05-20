"""
Copyright (c) 2024, Brian Ó Raghallaigh <brian.oraghallaigh@dcu.ie>
All rights reserved.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.

This script will abbreviate Irish language placenames to less than 20 characters if required, e.g. for NTA bus stop flags.
"""

import re

mutations_c4 = ['bhFl', 'bhFr']
mutations_c3 = ['Bhl', 'Bhr', 'mBl', 'mBr', 'Chl', 'Chn', 'Chr', 'gCl', 'gCn', 'gCr', 'Dhl', 'Dhn', 'Dhr', 'nDl', 'nDr', 'bhF', 'Fhl', 'Fhr', 'Ghl', 'Ghn', 'Ghr', 'nGl', 'nGn', 'nGr', 'Mhl', 'Mhr', 'Phl', 'Phr', 'bPl', 'bPr', 'tSl', 'tSn', 'tSr', 'Shl', 'Shn', 'Shr', 'Thl', 'Thn', 'Thr', 'dTl', 'dTn', 'dTr']
mutations_c2 = ['Bh', 'mB', 'Ch', 'gC', 'Dh', 'nD', 'Fh', 'Gh', 'nG', 'Mh', 'Ph', 'bP', 'tS', 'Sh', 'Th', 'dT']
mutations_v2 = ['hA', 'hÁ', 'nA', 'nÁ', 'tA', 'tÁ', 'hE', 'hÉ', 'nE', 'nÉ', 'tE', 'tÉ', 'hI', 'hÍ', 'nI', 'nÍ', 'tI', 'tÍ', 'hO', 'hÓ', 'nO', 'nÓ', 'tO', 'tÓ', 'hU', 'hÚ', 'nU', 'nÚ', 'tU', 'tÚ']

"""
Types of abbreviation:
- First letter
- First 2/3/4 letters
- Vowels removed
- First letter + last consonant (cluster) + optional -án/-ín
- First letter + medial consonant (cluster) + last consonant (cluster)
- Eclipsed initial vowel
- Initial vowel or 's' (cluster) with prefix 't'
- Lenited initial consonant (cluster) 
"""

# TODO: Check if there is consensus regarding how to abbreviate the following qualifiers and classifiers:

adjective_abbreviations = {
    'Thuaidh': 'Thu',
    'Theas': 'The',
    'Thoir': 'Tho',
    'Thiar': 'Thi',
    'Uachtarach': 'Uach',
    'Íochtarach': 'Íoch'
}

classifier_abbreviations = {
    'Abhainn': 'Abh',
    'Achadh': 'A',
    'Aill': 'Aill',
    'Áineasa': 'Áin',
    'Áineas': 'Áin',
    'Áirse': 'Áir',
    'An Ceathrú': 'An 4ú',
    'An Coláiste Ollscoile, Baile Átha Cliath': 'COBÁC',
    'An Chéad': 'An 1ú',
    'An Cúigiú': 'An 5ú',
    'An Dara': 'An 2ú',
    'An Deichiú': 'An 10ú',
    'An Naoú': 'An 9ú',
    'An tOchtú': 'An 8ú',
    'An Seachtú': 'An 7ú',
    'An Séú': 'An 6ú',
    'An Tríú': 'An 3ú',
    'Árasáin': 'Ára',
    'Ard-Oifig an Phoist': 'AOP',
    'Arda': 'Arda',
    'Ard': 'Ard',
    'Ardán': 'Ardn',
    'Ascaill': 'Asc',
    'Átha': 'Á',
    'Áth': 'Á',
    'Bá': 'Bá',
    'Baile': 'B',
    'Bailtíní': 'Btní',
    'Banc': 'Bnc',
    'Barr': 'Brr',
    'Beairic': 'Brc',
    'Béal': 'Bl',
    'Bealach': 'Bch',
    'Bearna': 'Brn',
    'Binn': 'Bnn',
    'Bóthar': 'Br',
    'Bruach': 'Brch',
    'Buaile': 'Bu',
    'Buirg': 'Brg',
    'Búlbhard': 'Blbhrd',
    'Bun': 'Bn',
    'Caiseal': 'Csl',
    'Caisleán': 'Cais',
    'Calafort': 'Cal',
    'Carn': 'Crn',
    'Carraig': 'Crg',
    'Ceanncheathrú': 'CC',
    'Ceann': 'Cnn',
    'Ceapach': 'Cp',
    'Cearnóg': 'Crng',
    'Ceathrú': 'C',
    'Cill': 'Cill',
    'Clochar': 'Clchr',
    'Clochán': 'Clchán',
    'Cloch': 'Clch',
    'Cluain': 'Cl',
    'Clár': 'Clr',
    'Clós': 'Cls',
    'Cnocán': 'Cncn',
    'Cnoc': 'Cn',
    #'Coill': 'Cll',
    'Coirnéal': 'Crnl',
    'Coisithe': 'Cois',
    'Coláiste': 'Col',
    'Comhairle': 'Crl',
    'Contae': 'Co',
    'Corrán': 'Crrn',
    'Corr': 'Crr',
    'Cosán': 'Cos',
    'Crois': 'X',
    'Crosaire': 'Cro',
    'Cuan': 'Cu',
    'Cuarbhóthar': 'CB',
    'Cumann Lúthchleas Gael': 'CLG',
    'Cumann Ríoga Bhaile Átha Cliath': 'RDS',
    'Currach': 'Crch',
    'Céide': 'Cde',
    'Cé': 'Cé',
    'Cúirt': 'Crt',
    'Daingean': 'Dngn',
    'Diméin': 'Dim',
    'Doire': 'Doi',
    'Domhnach': 'Domh',
    'Droichead': 'Dr',
    'Droim': 'Drm',
    'Dugaí': 'Dug',
    'Dumhcha': 'Dumh',
    'Dún': 'D',
    'Éadan': 'Éad',
    'Eaglais': 'Eag',
    'Eanach': 'Ean',
    'Eastát': 'Est',
    'Faiche': 'Fai',
    'Fearann': 'F',
    'Feirm': 'Fei',
    'Foirgnimh': 'Foi',
    'Gabhal': 'Gabh',
    'Gairdíní': 'Gdní',
    'Garraí': 'Garr',
    'Garrán': 'Grrn',
    'Geata': 'Gea',
    'Glas': 'Gls',
    'Glaise': 'Glse',
    'Gleann': 'Gl',
    'Gléib': 'Gb',
    'Goirtín': 'Gtn',
    'Gort': 'G',
    'Gráig': 'Gr',
    'Gráinseach': 'Gch',
    'Halla': 'H',
    'Iarnród': 'Inrd',
    'Inis': 'I',
    'Institiúid Teicneolaíochta': 'IT',
    'Íochtar': 'Íoch',
    'Ionad Baile': 'IB',
    'Ionad Siopadóireachta': 'IS',
    'Iostáin': 'Ios',
    'Iothlainn': 'Ioth',
    'Isteach': 'Ist',
    'Ladhar': 'Ldhr',
    'Leachta': 'Leachta',
    'Leacht': 'Leacht',
    #'Leac': 'Lc',
    'Leamhach': 'Lmhch',
    'Leamhán': 'Lmhán',
    'Leargain': 'Leargn',
    'Learga': 'Learga',
    'Leath': 'Lth',
    'Leitir': 'Ltr',
    'Lios': 'Ls',
    'Lisín': 'Lsín',
    'Loch': 'L',
    'Lorgain': 'Lrgn',
    'Lorga': 'Lrga',
    'Lána': 'Ln',
    'Lár': 'Lr',
    'Léana': 'Léa',
    'Léim': 'Léi',
    'Lóiste': 'Lói',
    'Machaire': 'Mch',
    'Maigh': 'Mgh',
    'Mainistir': 'Mstr',
    'Mainéar': 'Mai',
    'Malartán': 'Mlrt',
    'Maol': 'Ml',
    'Margadh': 'Mrg',
    'Móin': 'Mn',
    'Móinéar': 'Mói',
    'Móinín': 'Mói',
    'Muileann': 'M',
    'Mullach': 'Mull',
    'Mullaigh': 'Mllgh',
    'Mulláin': 'Mlln',
    'Mullán': 'Mlln',
    'Na Bráithre Críostaí': 'BC',
    'Naomh': 'N',
    'Oifig Poist': 'PO',
    'Oileán': 'Oil',
    'Ollscoil Chathair Bhaile Átha Cliath': 'OCBÁC',
    'Ollscoil Náisiúnta na hÉireann': 'ONÉ',
    'Ollscoil Teicneolaíochta Bhaile Átha Cliath': 'OTBÁC',
    'Ollscoil': 'Olls',
    'Ospidéal Choláiste na hOllscoile': 'OCO',
    'Ospidéal': 'Osp',
    'Óstaí': 'Óst',
    'Paráid': 'Pd',
    'Pasáiste': 'Pas',
    'Peile': 'Peile',
    'Pictiúrlann': 'Pclann',
    'Plásóg': 'Plsg',
    'Plás': 'Pl',
    'Pobail': 'Pbl',
    'Pobal': 'Pbl',
    'Poiblí ': 'Pblí',
    'Pointe': 'Pnt',
    'Poll': 'P',
    'Port': 'Prt',
    'Postoifig': 'PO',
    'Páirc': 'Prc',
    'Radharc': 'Rrc',
    'Rae': 'Rae',
    'Rinn': 'Rnn',
    'Rochtain': 'Rchtn',
    'Ros': 'Ros',
    'Ráithín': 'Rthín',
    'Ráth': 'Rth',
    'San': 'S',
    'Scabhat': 'Sca',
    'Scairt': 'Scrt',
    'Sceach': 'Sc',
    'Scoil': 'Scl',
    'Seachbhóthar': 'Sbhr',
    'Seascann': 'Scnn',
    'Seisceann': 'Scnn',
    'Séipéal': 'Séip',
    'Síneadh': 'Sín',
    'Siúlán': 'Sln',
    'Sliabh': 'Sbh',
    'Srath': 'Sth',
    'Sráidbhaile': 'Srbh',
    'Sráid': 'Sr',
    'Sruthán': 'Srthn',
    'Staid': 'Std',
    'Steach': 'Stch',
    'Stigh': 'Stgh',
    'Stáisiún': 'Stn',
    'Stáisiún Dóiteáin': 'Stn Dóit',
    'Stáisiún na nGardaí': 'Stn Gardaí',
    'Talamh': 'Tal',
    'Tamhnach': 'Tamh',
    'Taobh': 'Tbh',
    'Teach': 'Tch',
    'Teampall': 'Tmp',
    'Tigh': 'Tgh',
    'Tionsclaíoch': 'Tnsc',
    'Tobar': 'Tob',
    'Trá': 'Tr',
    'Tuaim': 'Tm',
    'Tuar': 'T',
    'Tulach': 'Tul',
    'Tír': 'Tír',
    'Tóchar': 'Tchr',
    'Tóin': 'Tn',
    'Uachtar': 'Uach',
    'Uaimh': 'Umh',
    'Úllord': 'Úlld'
}

test_input = ['Mainéar Uí Chuinneagáin', 'Machaire Uí Rabhartaigh', 'Leitir Mhic an Bhaird', 'Machaire an Ghainimh', 'Tamhnach an tSalainn', 'An Chraobhaigh Chaol', 'Fearann Uí Chearnaigh', 'Béal Átha an Trí Liag', 'Inis Uí Mhaolchluiche', 'Droim Mhic an Choill', 'Béal Átha na gCarraigíní', 'Fearann Uí Tharpaigh', 'Mainéar an Chaisleáin', 'Achadh Leachta Freáil', 'Carraig Mhachaire Rois', 'Coillín an tSrutháin', 'Cúil Uí Fhathartaigh', 'Béal Átha an Mhuilinn', 'Bealach Bhaile an Mhuilinn', 'Bealach an Tirialaigh', 'Béal Átha na nGabhar', 'Baile Chaisleán na nGeochagán', 'Carraig an Chaisleáin', 'Scoil Bhaile an Chaisleáin', 'Teach Bhaile Mhic Comhghaill', 'Lidl An Clochán Liath', 'Aldi An Clochán Liath', 'Béal an Átha Móir Thoir', 'Droichead an Bhuitléaraigh N3', 'Carraig Mhachaire Rois N2', 'Béal Átha Liag Thoir', 'Stáisiún an Mhuilinn Chearr', 'An Muileann gCearr N4', 'Páirc Ghnó Bhaile Átha Luain', 'Stáisiún Bhaile Átha Luain', 'Béal Átha Liag Thiar', 'Stáisiún an Chaisleáin Riabhaigh', 'Stáisiún Chora Droma Rúisc', 'Stáisiún Mhainistir na Búille', 'Bóthar Chnoc an Choiligh', 'Mulláin Choill na Leamhán', 'Céide Radharc na Páirce', 'Bóthar an Mhachaire Bhuí', 'Bóthar Bhaile Uí Dhúgáin', 'Céide Chill Easpaig Bhróin', 'Bóthar Bhaile Átha Cliath', 'Sráid Chaisleán na Mainge', 'Sráid an Gheata Thuaidh', 'Bóthar Chrois an Mhuilinn', 'Calafort Mhainistir na Búille']

# Regular expression to match with patterns like Bóthar na gCloch, Cúil Uí Fhathartaigh, etc.:
def_np_ptrn = re.compile('(\w+\s)(an|na|Ó|Ní|Uí|Mac|Nic|Mhic an|Mhic)(\s\w+)')

def abbreviate(name):
    # TODO: Try different replacement sequences to maximise length of abbreviated placename.
    name_abbr = name
    # If longer than 19 characters, abbreviate adjectives, e.g. Thuaidh > Thu:
    if len(name_abbr) > 19:
        for word, abbr in adjective_abbreviations.items():
            name_abbr = name_abbr.replace(word, abbr)
    # TODO: Restrict to whole words only.
    # If still longer than 19 characters, abbreviate classifiers, e.g. Baile > B:
    if len(name_abbr) > 19:
        for word, abbr in classifier_abbreviations.items():
            name_abbr = name_abbr.replace(word, abbr)
    # TODO: Make abbreviation less greedy, e.g. by removing suffixes first.
    # If still longer than 19 characters, abbreviate the last word in definite noun phrases to first sound(s), e.g. Bóthar na gCloch > Bóthar na gCl:
    if len(name_abbr) > 19:
        if re.search(def_np_ptrn, name_abbr):
            result = re.search(def_np_ptrn, name_abbr)
            def_np = result.group(0)
            words = def_np.split(' ')
            if words[-1][0:4] in mutations_c4:
                def_np_abbr = ' '.join(words[:-1]) + ' ' + words[-1][0:4]
            elif words[-1][0:3] in mutations_c3:
                def_np_abbr = ' '.join(words[:-1]) + ' ' + words[-1][0:3]
            elif words[-1][0:2] in mutations_c2 + mutations_v2:
                def_np_abbr = ' '.join(words[:-1]) + ' ' + words[-1][0:2]
            else:
                def_np_abbr = ' '.join(words[:-1]) + ' ' + words[-1][0:1]
            name_abbr = name_abbr.replace(def_np, def_np_abbr)
    # If still longer than 19 characters, abbreviate the last word to first sound(s):
    if len(name_abbr) > 19:
        words = name_abbr.split(' ')
        if words[-1][0:4] in mutations_c4:
            name_abbr = ' '.join(words[:-1]) + ' ' + words[-1][0:4]
        elif words[-1][0:3] in mutations_c3:
            name_abbr = ' '.join(words[:-1]) + ' ' + words[-1][0:3]
        elif words[-1][0:2] in mutations_c2 + mutations_v2:
            name_abbr = ' '.join(words[:-1]) + ' ' + words[-1][0:2]
        else:
            name_abbr = ' '.join(words[:-1]) + ' ' + words[-1][0:1]
    # If still longer than 19 characters, abbreviate another word longer than 3 characters in length, one at a time, while still longer than 19 characters:
    while len(name_abbr) > 19:
        words = name_abbr.split(' ')
        words_abbr = []
        abbr_done = False
        for word in words:
            if len(word) > 3 and not abbr_done:
                if word[0:4] in mutations_c4:
                    words_abbr.append(word[0:4])
                elif word[0:3] in mutations_c3:
                    words_abbr.append(word[0:3])
                elif word[0:2] in mutations_c2 + mutations_v2:
                    words_abbr.append(word[0:2])
                else:
                    words_abbr.append(word[0:1])
                abbr_done = True
            else:
                words_abbr.append(word)
        name_abbr = ' '.join(words_abbr)
    return name_abbr

# TODO: Input/output options:
for name in test_input:
    output = abbreviate(name)
    print(output + ' (' + str(len(output)) + ')')
