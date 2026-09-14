# Population DNA

**Interactive Demographic Fingerprints of the United States**

A full-screen, immersive geospatial laboratory that visualizes the *Demographic Triad* across the United States at state and county scales.

**Live App:** [https://sounny.github.io/population-dna/](https://sounny.github.io/population-dna/)

---

## The Demographic Triad

Every population has a unique fingerprint defined by three forces:

1. **Population Structure** (Upper-Left Arm): 18 five-year age-sex cohorts (0-4 through 85+) showing male (cyan) vs female (rose) population shares
2. **Mortality Schedule** (Upper-Right Arm): Life-course distribution of deaths by age and sex
3. **Fertility Timing** (Bottom Arm): Proportional Age-Specific Fertility Rate (PASFR) across reproductive cohorts 15-49

## Features

- **Full-screen immersive dark interface** with zero scrolling
- **Multi-scale vector map** (D3.js Albers USA projection) with cinematic zoom transitions
- **Dynamic county drill-down**: Click any state to reveal county boundaries, click counties to inspect
- **Ghost benchmark overlay**: National baseline appears behind local profiles
- **Curated story presets**: Utah (young/fertile), Florida (retirement), DC (urban singles), Texas, Maine (aging)
- **High-res PNG export** for LinkedIn and academic presentations
- **254 Texas counties** with full demographic triad data
- **All 50 states + DC** with Census PEP 2023 population estimates

## Data Sources

- U.S. Census Bureau Population Estimates Program (PEP 2023 Vintage)
- U.S. Census Bureau American Community Survey (ACS 5-Year)
- CDC National Center for Health Statistics (NCHS/NVSS)
- TopoJSON boundaries from US Atlas

## Author

Dr. Moulay Anwar Sounny-Slitine, Department of History & Geography, Texas Southern University

## License

MIT
