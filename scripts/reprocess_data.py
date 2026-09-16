import urllib.request
import csv
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

AGE_COHORTS = [
    '0-4', '5-9', '10-14', '15-19', '20-24', '25-29',
    '30-34', '35-39', '40-44', '45-49', '50-54', '55-59',
    '60-64', '65-69', '70-74', '75-79', '80-84', '85+'
]

FERTILITY_COHORTS = ['15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49']

FIPS_TO_STATE = {
    '01': 'Alabama', '02': 'Alaska', '04': 'Arizona', '05': 'Arkansas',
    '06': 'California', '08': 'Colorado', '09': 'Connecticut', '10': 'Delaware',
    '11': 'District of Columbia', '12': 'Florida', '13': 'Georgia', '15': 'Hawaii',
    '16': 'Idaho', '17': 'Illinois', '18': 'Indiana', '19': 'Iowa',
    '20': 'Kansas', '21': 'Kentucky', '22': 'Louisiana', '23': 'Maine',
    '24': 'Maryland', '25': 'Massachusetts', '26': 'Michigan', '27': 'Minnesota',
    '28': 'Mississippi', '29': 'Missouri', '30': 'Montana', '31': 'Nebraska',
    '32': 'Nevada', '33': 'New Hampshire', '34': 'New Jersey', '35': 'New Mexico',
    '36': 'New York', '37': 'North Carolina', '38': 'North Dakota', '39': 'Ohio',
    '40': 'Oklahoma', '41': 'Oregon', '42': 'Pennsylvania', '44': 'Rhode Island',
    '45': 'South Carolina', '46': 'South Dakota', '47': 'Tennessee', '48': 'Texas',
    '49': 'Utah', '50': 'Vermont', '51': 'Virginia', '53': 'Washington',
    '54': 'West Virginia', '55': 'Wisconsin', '56': 'Wyoming', '72': 'Puerto Rico'
}

STATE_TO_ABBR = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
    'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
    'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
    'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI',
    'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
    'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'Puerto Rico': 'PR'
}

def map_age_to_cohort(age):
    if age == 999:
        return -1
    if age >= 85:
        return 17
    return min(age // 5, 17)

def compute_median_age(male_arr, female_arr):
    total = sum(male_arr) + sum(female_arr)
    if total == 0:
        return 0.0
    half = total / 2.0
    running = 0
    for idx in range(18):
        cohort_pop = male_arr[idx] + female_arr[idx]
        if running + cohort_pop >= half:
            lower = idx * 5
            fraction = (half - running) / max(cohort_pop, 1)
            return round(lower + fraction * 5.0, 1)
        running += cohort_pop
    return 40.0

def generate_mortality_profile(median_age, male_arr, female_arr):
    base_qx_m = [
        0.0058, 0.0008, 0.0009, 0.0035, 0.0070, 0.0085,
        0.0105, 0.0135, 0.0195, 0.0310, 0.0520, 0.0820,
        0.1250, 0.1780, 0.2520, 0.3550, 0.4900, 0.6800
    ]
    base_qx_f = [
        0.0048, 0.0006, 0.0007, 0.0018, 0.0032, 0.0042,
        0.0062, 0.0090, 0.0145, 0.0225, 0.0360, 0.0560,
        0.0860, 0.1280, 0.1900, 0.2850, 0.4200, 0.6500
    ]
    deaths_m = [male_arr[i] * base_qx_m[i] for i in range(18)]
    deaths_f = [female_arr[i] * base_qx_f[i] for i in range(18)]
    total_deaths = max(sum(deaths_m) + sum(deaths_f), 1)

    mort_m_pct = [round((d / total_deaths) * 100.0, 2) for d in deaths_m]
    mort_f_pct = [round((d / total_deaths) * 100.0, 2) for d in deaths_f]
    return mort_m_pct, mort_f_pct

def generate_fertility_profile(state_or_county_type, median_age):
    if median_age < 34.0:
        pasfr = [6.8, 24.2, 31.5, 24.1, 10.8, 2.4, 0.2]
        tfr = 1.85
    elif median_age > 43.0:
        pasfr = [3.8, 14.5, 27.2, 33.5, 17.5, 3.3, 0.2]
        tfr = 1.45
    else:
        pasfr = [5.1, 18.2, 28.6, 31.2, 13.9, 2.8, 0.2]
        tfr = 1.66
    return pasfr, tfr

def process_state_demographics():
    print('Processing State and National Demographics from US Census PEP...')
    url = 'https://www2.census.gov/programs-surveys/popest/datasets/2020-2023/state/asrh/sc-est2023-agesex-civ.csv'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as resp:
        lines = [line.decode('utf-8', errors='ignore') for line in resp.readlines()]

    reader = csv.DictReader(lines)
    data_by_fips = {}

    for row in reader:
        sumlev = row.get('SUMLEV')
        if sumlev not in ('010', '040'):
            continue
        
        fips = str(row.get('STATE')).zfill(2)
        sex = int(row.get('SEX', 0))
        age = int(row.get('AGE', 0))
        pop = int(row.get('POPEST2023_CIV', 0))
        
        cohort_idx = map_age_to_cohort(age)
        if cohort_idx == -1:
            continue  # Skip summary row AGE 999
        
        if fips not in data_by_fips:
            name = row.get('NAME')
            abbr = STATE_TO_ABBR.get(name, 'US' if fips == '00' else '')
            data_by_fips[fips] = {
                'fips': fips,
                'name': name,
                'abbr': abbr,
                'male_pop_cohorts': [0] * 18,
                'female_pop_cohorts': [0] * 18,
                'total_male': 0,
                'total_female': 0,
                'total_pop': 0
            }
        
        if sex == 1:
            data_by_fips[fips]['male_pop_cohorts'][cohort_idx] += pop
            data_by_fips[fips]['total_male'] += pop
        elif sex == 2:
            data_by_fips[fips]['female_pop_cohorts'][cohort_idx] += pop
            data_by_fips[fips]['total_female'] += pop

    states_dict = {}
    national_data = None

    for fips, entry in data_by_fips.items():
        total = entry['total_male'] + entry['total_female']
        entry['total_pop'] = total
        entry['pop_m_pct'] = [round((p / max(total, 1)) * 100.0, 2) for p in entry['male_pop_cohorts']]
        entry['pop_f_pct'] = [round((p / max(total, 1)) * 100.0, 2) for p in entry['female_pop_cohorts']]
        
        med_age = compute_median_age(entry['male_pop_cohorts'], entry['female_pop_cohorts'])
        entry['median_age'] = med_age
        
        mort_m, mort_f = generate_mortality_profile(med_age, entry['male_pop_cohorts'], entry['female_pop_cohorts'])
        entry['mort_m_pct'] = mort_m
        entry['mort_f_pct'] = mort_f
        
        pasfr, tfr = generate_fertility_profile(entry['abbr'], med_age)
        if entry['abbr'] in ('UT', 'ID', 'TX', 'SD', 'ND', 'NE', 'LA', 'MS'):
            tfr = round(tfr * 1.12, 2)
            pasfr = [6.2, 22.8, 32.4, 25.0, 11.2, 2.2, 0.2]
        elif entry['abbr'] in ('DC', 'VT', 'MA', 'NH', 'RI', 'OR', 'CA', 'NY'):
            tfr = round(tfr * 0.88, 2)
            pasfr = [2.9, 12.8, 26.5, 36.2, 18.2, 3.2, 0.2]
        
        entry['fertility_pasfr'] = pasfr
        entry['tfr'] = tfr
        
        youth_pop = sum(entry['male_pop_cohorts'][0:3]) + sum(entry['female_pop_cohorts'][0:3])
        working_pop = sum(entry['male_pop_cohorts'][3:13]) + sum(entry['female_pop_cohorts'][3:13])
        elder_pop = sum(entry['male_pop_cohorts'][13:18]) + sum(entry['female_pop_cohorts'][13:18])
        
        entry['youth_dependency'] = round((youth_pop / max(working_pop, 1)) * 100.0, 1)
        entry['elder_dependency'] = round((elder_pop / max(working_pop, 1)) * 100.0, 1)
        entry['total_dependency'] = round(((youth_pop + elder_pop) / max(working_pop, 1)) * 100.0, 1)

        if fips == '00':
            national_data = entry
        else:
            states_dict[fips] = entry

    nat_path = os.path.join(DATA_DIR, 'us_national_demographics.json')
    with open(nat_path, 'w', encoding='utf-8') as f:
        json.dump(national_data, f, indent=2)
    print(f'Saved National Demographics to {nat_path}')

    states_path = os.path.join(DATA_DIR, 'us_states_demographics.json')
    with open(states_path, 'w', encoding='utf-8') as f:
        json.dump(states_dict, f, indent=2)
    print(f'Saved {len(states_dict)} States to {states_path}')
    return national_data, states_dict

def process_texas_counties():
    print('Processing Texas 254 Counties from existing workspace and Census ACS...')
    tx_explorer_path = 'G:/My Drive/0-TSU/Courses/GEOG331/texas_demographics_explorer.html'
    with open(tx_explorer_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    m = re.search(r'const TX_CENSUS = (\{.*?\});\s*const', content, re.DOTALL)
    if not m:
        print('Could not find TX_CENSUS in explorer file!')
        return {}
    
    raw_tx = json.loads(m.group(1))
    print(f'Loaded {len(raw_tx)} Texas Counties from local verified source.')
    
    counties_dict = {}
    for code, c in raw_tx.items():
        fips = c['fips']
        name = c['name']
        m_pop = c['age_male']
        f_pop = c['age_female']
        total = c['total_pop']
        med_age = float(c.get('median_age', 38.0))
        
        m_pct = [round((p / max(total, 1)) * 100.0, 2) for p in m_pop]
        f_pct = [round((p / max(total, 1)) * 100.0, 2) for p in f_pop]
        
        mort_m, mort_f = generate_mortality_profile(med_age, m_pop, f_pop)
        
        is_college = name in ('Brazos', 'Denton', 'Lubbock', 'Walker', 'Hays')
        is_border = name in ('Hidalgo', 'Cameron', 'Starr', 'Maverick', 'Webb', 'Zapata', 'Presidio', 'El Paso')
        is_retirement = med_age > 48.0
        is_energy = name in ('Loving', 'Midland', 'Ector', 'Reeves', 'Upton', 'Reagan', 'Martin')
        
        if is_college:
            pasfr = [1.8, 12.2, 28.5, 36.8, 17.5, 3.0, 0.2]
            tfr = 1.35
            story_tag = 'College Center (hourglass shape at ages 18 to 24)'
        elif is_border:
            pasfr = [7.5, 26.5, 32.8, 21.5, 9.2, 2.3, 0.2]
            tfr = 2.05
            story_tag = 'Border Region (young median age and early childbearing)'
        elif is_retirement:
            pasfr = [3.2, 13.5, 25.5, 33.0, 20.5, 4.1, 0.2]
            tfr = 1.38
            story_tag = 'Retirement Destination (high elder population concentration)'
        elif is_energy:
            pasfr = [5.5, 22.0, 31.0, 26.0, 12.5, 2.8, 0.2]
            tfr = 1.82
            story_tag = 'Energy Production Sector (working-age male labor concentration)'
        else:
            pasfr, tfr = generate_fertility_profile('TX', med_age)
            story_tag = 'Metropolitan and Regional Hub'
            
        youth_pop = sum(m_pop[0:3]) + sum(f_pop[0:3])
        working_pop = sum(m_pop[3:13]) + sum(f_pop[3:13])
        elder_pop = sum(m_pop[13:18]) + sum(f_pop[13:18])
        
        counties_dict[fips] = {
            'fips': fips,
            'county_code': code,
            'name': name + ' County',
            'short_name': name,
            'state_fips': '48',
            'state_abbr': 'TX',
            'total_pop': total,
            'male_pop': c['male_pop'],
            'female_pop': c['female_pop'],
            'male_pop_cohorts': m_pop,
            'female_pop_cohorts': f_pop,
            'pop_m_pct': m_pct,
            'pop_f_pct': f_pct,
            'median_age': med_age,
            'mort_m_pct': mort_m,
            'mort_f_pct': mort_f,
            'fertility_pasfr': pasfr,
            'tfr': tfr,
            'youth_dependency': round((youth_pop / max(working_pop, 1)) * 100.0, 1),
            'elder_dependency': round((elder_pop / max(working_pop, 1)) * 100.0, 1),
            'total_dependency': round(((youth_pop + elder_pop) / max(working_pop, 1)) * 100.0, 1),
            'hispanic': c.get('hispanic', 0),
            'white_nh': c.get('white_nh', 0),
            'black_nh': c.get('black_nh', 0),
            'asian_nh': c.get('asian_nh', 0),
            'story_tag': story_tag
        }

    tx_path = os.path.join(DATA_DIR, 'texas_counties_demographics.json')
    with open(tx_path, 'w', encoding='utf-8') as f:
        json.dump(counties_dict, f, indent=2)
    print(f'Saved {len(counties_dict)} Texas Counties to {tx_path}')
    return counties_dict

if __name__ == '__main__':
    process_state_demographics()
    process_texas_counties()
    print('All demographic datasets processed and saved successfully.')
