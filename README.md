# Pokemon TCG Card Comparison Tool

A Streamlit-based web application for comparing Pokemon Trading Card Game (TCG) cards, analyzing their stats, and evaluating their efficiency.

## Features

- **Card Database**: Comprehensive collection of Pokemon TCG cards with detailed information
- **Card Comparison**: Side-by-side comparison of multiple cards
- **Stat Analysis**: Detailed analysis of card stats including:
  - HP (Hit Points)
  - Attack Power
  - Energy Requirements
  - Retreat Cost
  - Card Type
  - Weakness/Resistance
- **Efficiency Metrics**: Calculation of card efficiency based on:
  - Damage per Energy
  - HP to Retreat Cost ratio
  - Overall card value

## Setup

1. Clone the repository:
```bash
git clone [your-repository-url]
cd pokemon-tcg-comparison
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
pokemon-tcg-comparison/
├── app.py              # Main Streamlit application
├── data/              # Card database and scraped data
├── utils/             # Utility functions for data processing
├── requirements.txt   # Project dependencies
└── README.md         # Project documentation
```

## Data Collection

The application uses web scraping to collect card data from official Pokemon TCG sources. The data collection process includes:

- Card images
- Card stats and attributes
- Card text and effects
- Market prices (if available)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Pokemon TCG API
- Streamlit for the web framework
- Pokemon Company for card data
