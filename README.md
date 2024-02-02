# metric-atlas
 An open source metrics explorer built with Streamlit.

> This project is a work in progress...

## Getting Started
1. Install requirements `pip install -r requirements.txt`
2. Initialize the local Duck DB with seed data (or add your own) `python db/init.py`
3. Start the streamlit app `streamlit run home.py`
4. Configure metrics in `config/sample.yml`

## Configuration
Some configuration for the app can be set in the `config/config.yml`

## Linting and Formatting
```
black app/
flake8 app/
bandit -r app/
```