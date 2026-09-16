# Demographic Fingerprints

**Interactive Population Profiles of the United States**

A full-screen, immersive geospatial laboratory that visualizes the Demographic Triad across the United States at national, state, and county scales.

**Live App:** [https://sounny.github.io/demographic-fingerprints/](https://sounny.github.io/demographic-fingerprints/)

### The Demographic Triad

Every population possesses a distinctive demographic fingerprint defined by three foundational forces:

1. **Population Structure** (Upper-Left Arm): 18 five-year age-sex cohorts (0 to 4 through 85+) illustrating male (cyan) versus female (rose) population shares.
2. **Mortality Schedule** (Upper-Right Arm): Life-course distribution of mortality by age and sex, calibrated with CDC life table actuarial schedules.
3. **Fertility Timing** (Bottom Arm): Proportional Age-Specific Fertility Rate (PASFR) across reproductive cohorts (ages 15 to 49).

### Features

- **Full-Screen Immersive Interface**: Zero scrolling with adaptive vector canvas.
- **Multi-Scale Vector Geography**: D3.js Albers USA projection with smooth state transitions.
- **Faint Background County Layer**: Reveals county boundaries when zoomed into any state, enabling interactive mouseover tooltips and county selection.
- **Calibrated Tri-Axial Glyph**: Explicit milestone age labels (0-4, 20-24, 40-44, 65-69, 85+) and fertility cohort tags with interactive hover inspection.
- **National Benchmark Ghost**: Dashed baseline overlay for instant local-to-national comparative analysis.
- **Curated Exploration Presets**: Utah (Young & Fertile), Florida (Aging & Retirement), District of Columbia (Urban Singles), Texas (Rapid Growth), Maine (Oldest Median Age), and California (Diverse Metro).
- **High-Resolution PNG Export**: Direct client-side visual capture for presentations and publications.
- **254 Texas Counties**: Granular demographic triad profiles with specialized socioeconomic tags.
- **All 50 States and DC**: Official U.S. Census Bureau PEP 2023 demographic distributions.

### Data Sources

- U.S. Census Bureau Population Estimates Program (PEP 2023 Vintage)
- U.S. Census Bureau American Community Survey (ACS 5-Year Estimates)
- CDC National Center for Health Statistics (NCHS/NVSS)
- TopoJSON cartographic boundaries from US Atlas

### Author

Dr. Moulay Anwar Sounny-Slitine

### License

MIT
