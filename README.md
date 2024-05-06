
# Telfer Scenario Technical Dashboard Artifact

This repo holds the code and required files to run the Technical Dashboard artifact for the Telfer Scenario - Zelonia (May 9th, 2024),


## Run Locally
### Step 1: Clone the project
Clone the project using the command:
```bash
git clone https://github.com/UOttawa-Cyber-Range-Scenarios/telfer-zelonia-scenario.git
```
Go to the project directory

```bash
  cd telfer-zelonia-scenario
```

### Step 2: Install dependencies
Install the required packages using the command:
```bash
pip install -r requirements.txt
```

### Step 3: Run the project
Run the project on ```localhost``` and ```localnetwork``` using the command:
```
cd Zelonia
streamlit run app.py
``` 
Streamlit will provide the localhost URL and the network URL once the app starts running

### Step 4: Access the admin panel to interact with the dashboard
1) Go to the app in the browser.
2) Expand the sidebar on the left.
3) Login using the following credentials:
```
user: admin
password: password
```

4) Modify the values in the admin panel and see it reflect on the dashboard!
5) Open another instance of the dashboard in a new tab. Changes in the admin panel in the original instance will be reflected in the new instance as well. You can share this new instance so that the admin panel is not visible to the participants.



