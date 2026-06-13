-- Referenssidata: lajit, maakunnat, suurimmat kaupungit

INSERT INTO sports (id, slug, name_fi, name_en) VALUES
    (1,  'jalkapallo',    'Jalkapallo',           'Football'),
    (2,  'jaakiekko',     'Jääkiekko',            'Ice hockey'),
    (3,  'salibandy',     'Salibandy',            'Floorball'),
    (4,  'golf',          'Golf',                 'Golf'),
    (5,  'voimistelu',    'Voimistelu',           'Gymnastics'),
    (6,  'koripallo',     'Koripallo',            'Basketball'),
    (7,  'lentopallo',    'Lentopallo',           'Volleyball'),
    (8,  'pesapallo',     'Pesäpallo',            'Finnish baseball'),
    (9,  'uinti',         'Uinti',                'Swimming'),
    (10, 'yleisurheilu',  'Yleisurheilu',         'Athletics'),
    (11, 'tennis',        'Tennis',               'Tennis'),
    (12, 'purjehdus',     'Purjehdus',            'Sailing'),
    (13, 'ratsastus',     'Ratsastus',            'Equestrian'),
    (14, 'pyoraily',      'Pyöräily',             'Cycling'),
    (15, 'suunnistus',    'Suunnistus',           'Orienteering'),
    (16, 'hiihto',        'Hiihto',               'Skiing'),
    (17, 'kasiapallo',    'Käsipallo',            'Handball'),
    (18, 'kamppailulajit','Kamppailulajit',       'Martial arts'),
    (19, 'frisbeegolf',   'Frisbeegolf',          'Disc golf'),
    (20, 'padel',         'Padel',                'Padel');

INSERT INTO sport_aliases (sport_id, alias) VALUES
    (1,  'football'), (1,  'futsal'),
    (2,  'jääkiekko'), (2,  'ice hockey'), (2,  'hockey'),
    (3,  'floorball'), (3,  'unihockey'),
    (4,  'golf'),
    (5,  'voimistelu'), (5,  'gymnastics'), (5,  'cheerleading'),
    (6,  'basketball'), (7,  'volleyball'), (8,  'pesis'), (8,  'pesäpallo');

INSERT INTO regions (code, name) VALUES
    ('01', 'Ahvenanmaa'), ('02', 'Etelä-Karjala'), ('03', 'Etelä-Pohjanmaa'),
    ('04', 'Etelä-Savo'), ('05', 'Kainuu'), ('06', 'Kanta-Häme'),
    ('07', 'Keski-Pohjanmaa'), ('08', 'Keski-Suomi'), ('09', 'Kymenlaakso'),
    ('10', 'Lappi'), ('11', 'Pirkanmaa'), ('12', 'Pohjanmaa'),
    ('13', 'Pohjois-Karjala'), ('14', 'Pohjois-Pohjanmaa'), ('15', 'Pohjois-Savo'),
    ('16', 'Päijät-Häme'), ('17', 'Satakunta'), ('18', 'Uusimaa'),
    ('19', 'Varsinais-Suomi');

INSERT INTO municipalities (code, name, region_code) VALUES
    ('091', 'Helsinki',     '18'), ('092', 'Vantaa',       '18'),
    ('049', 'Espoo',        '18'), ('837', 'Tampere',      '11'),
    ('853', 'Turku',        '19'), ('564', 'Oulu',         '14'),
    ('179', 'Jyväskylä',    '08'), ('398', 'Lahti',        '16'),
    ('297', 'Kuopio',       '15'), ('609', 'Porvoo',       '18'),
    ('271', 'Joensuu',      '13'), ('405', 'Lappeenranta', '02'),
    ('109', 'Hämeenlinna',  '06'), ('905', 'Vaasa',        '12'),
    ('743', 'Seinäjoki',    '03'), ('684', 'Pori',         '17'),
    ('286', 'Kotka',        '09'), ('491', 'Mikkeli',      '04'),
    ('698', 'Rovaniemi',    '10');
