# TreatiseAI

TreatiseAI is a legal research and writing tool built on the the OpenAI API. It requires an OpenAI API key and uses the [Flask](https://flask.palletsprojects.com/en/2.0.x/) web framework. Follow the instructions below to get set up.

TreatiseAI is available as a web demo at [treatiseai.com](https://www.treatiseai.com)
Email info@clearlayer.com for credentials, describing your use for the tool

## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/)

2. Clone this repository

3. Navigate into the project directory

   ```bash
   $ cd treatise-ai
   ```

4. Create a new virtual environment

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Install the requirements

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file

   ```bash
   $ cp .env.example .env
   ```

7. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file

8. Run the app

   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://localhost:5000](http://localhost:5000).
