
GOVERNMENT_TYPE = (
        ('ministry_offices', 'Ministry offices',),
        ('universities', 'Universities',),
        ('Other', 'Other',),
    )
    
GENDER_CHOICES = ((0,'Male'),(1,'Female'))

INVESTMENT_TYPE_CHOICES = (
    
        ('selection', 'selection',),
        ('finance', 'finance',),
        ('working_space', 'working space',),
        ('material', 'material',),
        ('Other', 'Other',),
    )

LEVEL = (
        ('pre', 'Pre-Startup',),
        ('mid', 'Mid-Startup',),
        ('early', 'Early Trsction',),
        ('post', 'Post startup',),
    )

STARTUP_STAGE = (
        ("pre", "Pre-Startup",),
        ("mid", "Mid-Startup",),
        ("early", "Early Trsction",),
        ("market", "In-Market",),
    )
PROGRAM_DURATION = (
        ('less_than_3_month', 'less than 3 month',),
        ('3_to_6_months', '3 to 6 months',),
        ('6_months_to_a_year', '6 months to a year',),
        ('1_year_to_two_years', '1 year to two years',),
        ('International', 'International',),
    )
FUNDED_BY_CHOICES = (
        ('self_', 'self',),
        ('government', 'government',),
        ('nGO', 'NGO',),
        ('grant', 'Grant',),
        ('International', 'International',),
         ('Other', 'Other',),
    )
Private = 'Private'
Public = 'Public'
nGO = 'NGO'
Government = 'Government'
Other = 'Other'
OWNERSHIP = [
        (Private, 'Private'),
        (Public, 'Public'),
        (nGO, 'NGO'),
        (Government, 'Government'),
        (Other, 'Other'),
        
    ]

Accelerator = 'Accelerator'
Incubation = 'Incubation'
Hub = 'Hub'
SERVICE_TYPE = [
        (Accelerator, 'Accelerator'),
        (Incubation, 'Incubation'),
        (Hub, 'Hub'),
        
    ]
Domestic = 'Domestic'
International = 'International'  
MARKET_SCOPE = [
        (Domestic, 'Domestic'),
        (International, 'International'),
        
    ]

pre_market='pre start-up( early-stage)'
mid_startup = 'mid start-up'
in_startuo = 'in-market'  

STAGE = [
        (pre_market, 'pre start-up( early-stage)'),
        (mid_startup, 'mid start-up'),
        (in_startuo, 'in-market'),
        
    ]
Entertainment ='Entertainment'
Energy ='Energy'
Logistics ='Logistics'
Construction  ='Construction'
Health ='Health'
Manufacturing ='Manufacturing'
Cleaning='Cleaning'
Education  ='Education'
Finance ='Finance'
Tourism='Tourism' 
Other='Other' 
iT='IT'
Agriculture='Agriculture'

SECTORS = [
        (Entertainment, 'Entertainment'),
        (Energy, 'Energy'),
        (Logistics, 'Logistics'),
        (Construction, 'Construction'),
        (Education, 'Education'),
        (Health, 'Health'),
        (Manufacturing, 'Manufacturing'),
        (Cleaning, 'Cleaning'),
        (Education, 'Education'),
        (Finance, 'Finance'),
        (Tourism, 'Tourism'),
        (iT, 'IT'),
        (Agriculture, 'Agriculture'),
        (Other, 'Other'),
        
    ]

selectr= "Please Select Region"
adissAbeba ='Addis Ababa'
afar ='Afar'
amhara ='Amhara'
benishangulgumuz  ='Benishangul-Gumuz'
diredawa ='Dire Dawa'
gambela ='Gambela'
harari='Harari'
oromia  ='Oromia'
somali ='Somali'
sidama='Sidama' 
southwest='South West Peoples' 
snnp='SNNP'
tigray='Tigray'


REGIONS_CHOICES = [
        (adissAbeba, 'Addis Ababa'),
        (afar, 'Afar'),
        (amhara, 'Amhara'),
        (benishangulgumuz, 'Benishangul-Gumuz'),
        (diredawa, 'Dire Dawa'),
        (gambela, 'Gambela'),
        (harari, 'Harari'),
        (oromia, 'Oromia'),
        (somali, 'Somali'),
        (sidama, 'Sidama '),
        (southwest, 'South West'),
        (snnp, 'SNNP'),
        (tigray, 'Tigray'),
        
    ]

EDUCATIONAL_LEVEL = [
        ('no_formal_education', 'No formal education'),
        ('primary_education', 'Primary education'),
        ('secondary_education_or_high_school', 'Secondary education or high school'),
        ('vocational_qualification', 'Vocational qualification'),
        ('bachelors_degree','Bachelors degree'),
        ('masters_degree', 'Masters degree'),
        ('doctorate_or_higher','Doctorate or higher'),
        ('other','Other'),
        
    ]
EDUCATIONAL_BACKGROUND = [
    ('arts_and_humanities', 'Arts and humanities'),
        ('business_and_management', 'Business and management'),
        ('computer_science', 'Computer science'),
        ('education', 'Education'),
        ('engineering','Engineering'),
        ('health', 'Health'),
        ('law','Law'),
        ('social_sciences','Social sciences'),
        ('natural_sciences','Natural sciences'),
        ('other','Other'),


]
MENTORSHIP_AREA = [
    ('legal_advice', 'legal advice'),
    ('business_model', 'business model'),
    ('innovation_management', 'innovation management'),
    ('intellectual_property', 'intellectual property'),
    ('other','Other'),
]









  
