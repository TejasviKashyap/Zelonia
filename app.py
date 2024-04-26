import streamlit as st
from PIL import Image
import random
import folium
from folium.plugins import TimestampedGeoJson
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go


st.set_page_config(
   page_title="Zelonia Systems Dashboard",
   page_icon="🧊",
   layout="wide"
)

# Function to get admin controls
#@st.cache(allow_output_mutation=True)
@st.cache_resource()
def get_admin_controls():
    return {
        "Navigation": "Online",
        "Weather": "Online",
        "Email": "Online",
        "HR": "Online",
        "Finance": "Online",
        "Pay": "Online"
    }

# Function to get admin inputs
#@st.cache(allow_output_mutation=True)
@st.cache_resource()
def get_admin_inputs():
    return {
        "num_affected_points": {
            'server1': 'Online',
            'server2': 'Online',
            'server3': 'Online'
        },
        "attack_server_found": False
    }

# Function to simulate scanning process
def scan_file_storage(system_name, status):
    # Simulate scanning process
    scanned_results = {}

    # Define file extension percentages for each system
    file_extensions = {
        "Navigation": {"shp": 56, "gpx": 21, "shx": 19, "geojson": 3, "csv": 1},
        "Weather": {"json": 40, "csv": 30, "txt": 20, "xml": 5, "grib": 3, "dat": 2},
        "Email": {"eml": 50, "msg": 30, "pst": 10, "mbox": 5, "pdf": 3, "docx": 2},
        "HR": {"pdf": 45, "docx": 30, "xlsx": 10, "csv": 7, "txt": 5, "jpg": 3},
        "Finance": {"xlsx": 50, "pdf": 20, "csv": 15, "docx": 10, "xml": 3, "json": 2},
        "Pay": {"pdf": 50, "xlsx": 25, "csv": 10, "docx": 8, "xml": 5, "json": 2}
    }

    if status == "Online":
        # For online systems, return the predefined file extension percentages
        scanned_results = file_extensions.get(system_name, {})
    else:
        # For offline systems, simulate SPIKE percentage between 90 and 97
        spike_percentage = random.randint(80, 90)
        scanned_results["SPIKE"] = spike_percentage

        # Distribute the rest among other file extensions
        total_percentage = 100 - spike_percentage
        other_extensions = file_extensions.get(system_name, {})
        for extension, percentage in other_extensions.items():
            scanned_results[extension] = percentage * total_percentage // 100

    return scanned_results

# Function to display pie charts for file extensions
def display_pie_charts(system_name, results):
    st.subheader(f"File Extensions for {system_name}")

    # Create a list of colors for the pie chart
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # Create a Pie chart using Plotly
    fig = go.Figure(data=[go.Pie(labels=list(results.keys()), values=list(results.values()), textinfo='label+percent', marker=dict(colors=colors))])
    fig.update_layout(title=f"File Extensions for {system_name}")
    
    # Render the Plotly chart
    st.plotly_chart(fig)

def create_new_map(num_affected_points, show_attack_server):
    # Create a Folium map centered at Singapore
    m = folium.Map(location=[1.3521+5, 103.8198+120], zoom_start=11, tiles='Cartodb dark_matter')

    # Add outline of Singapore as GeoJSON overlay
    folium.GeoJson(os.path.join("data", "output.geojson"), name="geojson").add_to(m)
    folium.GeoJson(os.path.join("data", "newoutput.geojson"), name="geojson2").add_to(m)

    servers=[ [[1.3521, 103.8198],
        [1.3578, 103.9870],
        [1.3196, 103.8253],
        [1.2901, 103.8029],[1.2865, 103.8539], [1.3242, 103.8744],
        [1.3575, 103.7640],
        [1.3667, 103.7744],
        [1.3967, 103.70]],[[1.2912, 103.8375],
        [1.3480, 103.6830],
        [1.3139, 103.7657],[1.2984, 103.7736],
        [1.3340, 103.7359],
        [1.3199, 103.7655],
        [1.3151, 103.7480],
        [1.3329, 103.7065],
        [1.2996, 103.8334],
        [1.2831, 103.8165]
        ],[[1.388307, 103.890594],
        [1.426724, 103.813737],
        [1.280952, 103.813019],
        [1.268026, 103.628778]
]
    ]

    for i in servers:
        for singapore_coordinates in i:
            singapore_coordinates[0] += 5
            singapore_coordinates[1] += 120

    # Define headquarters points
    headquarters = [[1.320+5, 103.8901+120],[1.3104+5, 103.7151+120], [1.261204+5, 103.669720+120]]
    
        # Add connections between headquarters points and other points on the map

    for i in range(3):
        server_status = num_affected_points['server'+str(i+1)]
        if server_status == 'Online':
            hq = headquarters[i]
            folium.Marker(location=hq, icon=folium.Icon(icon='fa-building', prefix='fa', color='blue', icon_color='black')).add_to(m)
            for point in servers[i]:
                folium.Marker(location=point, icon=folium.Icon(icon='fa-server', prefix='fa',color='lightgreen', icon_color='black')).add_to(m)
                folium.PolyLine(locations=[hq, point], color='lightgreen').add_to(m)
        elif server_status == 'Isolated':
            hq = headquarters[i]
            folium.Marker(location=hq, icon=folium.Icon(icon='fa-building', prefix='fa',color='lightgray')).add_to(m)
            for point in servers[i]:
                folium.Marker(location=point, icon=folium.Icon(icon='fa-server', prefix='fa',color='lightgray')).add_to(m)
                #folium.PolyLine(locations=[hq, point], color='green').add_to(m)
        else:
            hq = headquarters[i]
            folium.CircleMarker(location=hq, radius=10, color='black', fill=True, fill_color='red', fill_opacity=0.5).add_to(m)
            for point in servers[i]:
                folium.CircleMarker(location=point, radius=4, color='black', fill=True, fill_color='red', fill_opacity=0.5).add_to(m)
                folium.PolyLine(locations=[point, hq], color='red', weight=2).add_to(m)

    if show_attack_server:
        folium.CircleMarker(location=[7.354704-60, 80.990871-100], radius=10, color='red', fill=True, fill_color='red').add_to(m)
        for i in range(2):
            folium.PolyLine(locations=[[7.354704-60, 80.990871-100], headquarters[i]], color='red', weight=2).add_to(m)

    # Add JavaScript for blinking effect
    script = """
    <script>
    setInterval(function() {
        var dots = document.querySelectorAll('.leaflet-interactive[fill-opacity="0.5"]');
        for (var i = 0; i < dots.length; i++) {
            dots[i].style.display = (dots[i].style.display === 'none' ? '' : 'none');
        }
    }, 500);
    </script>
    """
    m.get_root().html.add_child(folium.Element(script))

    # Convert Folium map to HTML
    map_html = m._repr_html_()

    return map_html

def create_device_map(num_affected_points, show_attack_server):
    # Create a Folium map centered at Singapore
    m = folium.Map(location=[1.3521-20, 103.8198+100], zoom_start=11, tiles='Cartodb dark_matter')

    # Add outline of Singapore as GeoJSON overlay
    folium.GeoJson(os.path.join("data", "output.geojson"), name="geojson").add_to(m)
    folium.GeoJson(os.path.join("data", "newoutput.geojson"), name="geojson2").add_to(m)

    servers=[ [[1.3521, 103.8198],
        [1.3578, 103.9870],
        [1.3196, 103.8253],
        [1.2901, 103.8029],[1.2865, 103.8539], [1.3242, 103.8744],
        [1.3575, 103.7640],
        [1.3667, 103.7744],
        [1.3967, 103.70]],[[1.2912, 103.8375],
        [1.3480, 103.6830],
        [1.3139, 103.7657],[1.2984, 103.7736],
        [1.3340, 103.7359],
        [1.3199, 103.7655],
        [1.3151, 103.7480],
        [1.3329, 103.7065],
        [1.2996, 103.8334],
        [1.2831, 103.8165]
        ],[[1.388307, 103.890594],
        [1.426724, 103.813737],
        [1.280952, 103.813019],
        [1.268026, 103.628778]
]
    ]

    for i in servers:
        for singapore_coordinates in i:
            singapore_coordinates[0] += 5
            singapore_coordinates[1] += 120

    # Define headquarters points
    headquarters = [[1.320-20, 103.8901+100],[1.3104-20, 103.7151+100], [1.261204-20, 103.669720+100]]
    
        # Add connections between headquarters points and other points on the map

    for i in range(3):
        server_status = num_affected_points['server'+str(i+1)]
        if server_status == 'Online':
            hq = headquarters[i]
            folium.Marker(location=hq, icon=folium.Icon(icon='fa-building', prefix='fa', color='blue', icon_color='black')).add_to(m)
            for point in servers[i]:
                folium.Marker(location=point, icon=folium.Icon(icon='fa-server', prefix='fa',color='lightgreen', icon_color='black')).add_to(m)
                folium.PolyLine(locations=[hq, point], color='lightgreen').add_to(m)
        elif server_status == 'Isolated':
            hq = headquarters[i]
            folium.Marker(location=hq, icon=folium.Icon(icon='fa-building', prefix='fa',color='lightgray')).add_to(m)
            for point in servers[i]:
                folium.Marker(location=point, icon=folium.Icon(icon='fa-server', prefix='fa',color='lightgray')).add_to(m)
                #folium.PolyLine(locations=[hq, point], color='green').add_to(m)
        else:
            hq = headquarters[i]
            folium.CircleMarker(location=hq, radius=10, color='black', fill=True, fill_color='red', fill_opacity=0.5).add_to(m)
            for point in servers[i]:
                folium.CircleMarker(location=point, radius=4, color='black', fill=True, fill_color='red', fill_opacity=0.5).add_to(m)
                folium.PolyLine(locations=[point, hq], color='red', weight=2).add_to(m)

    if show_attack_server:
        folium.CircleMarker(location=[7.354704-60, 80.990871-100], radius=10, color='red', fill=True, fill_color='red').add_to(m)
        for i in range(2):
            folium.PolyLine(locations=[[7.354704-60, 80.990871-100], headquarters[i]], color='red', weight=2).add_to(m)

    # Add JavaScript for blinking effect
    script = """
    <script>
    setInterval(function() {
        var dots = document.querySelectorAll('.leaflet-interactive[fill-opacity="0.5"]');
        for (var i = 0; i < dots.length; i++) {
            dots[i].style.display = (dots[i].style.display === 'none' ? '' : 'none');
        }
    }, 500);
    </script>
    """
    m.get_root().html.add_child(folium.Element(script))

    # Convert Folium map to HTML
    map_html = m._repr_html_()

    return map_html


# Function to display system health details
def display_system_health(system_name, system_status):
    if system_status == "Online":
        st.success(f"{system_name} is Online")
        # Display system health graphics
        system_health = random.randint(96, 100)  # Random system health value (96 to 100)
        st.write(f"System Health: {system_health}%")
        my_bar = st.progress(0)

        for percent_complete in range(system_health):
            time.sleep(0.02)
            my_bar.progress(percent_complete + 1)

        # Generate random values for additional parameters for online systems
        active_instances = random.randint(20, 30)  # Random number of active instances (20 to 30)
        monitoring_services = random.randint(5, 10)  # Random number of monitoring services (5 to 10)
        response_time = random.uniform(50, 100)  # Random response time (50 to 100 ms)
        resource_utilization = random.uniform(60, 80)  # Random resource utilization (60% to 80%)
        service_availability = random.uniform(99.5, 99.9)  # Random service availability (99.5% to 99.9%)
        throughput = random.uniform(50, 100)  # Random throughput (50 to 100 Mbps)
        db_connections = random.randint(100, 150)  # Random number of database connections (100 to 150)
        network_traffic = random.uniform(100, 200)  # Random network traffic (100 to 200 GB)

        # Display additional parameters in a table format
        st.write("Additional Parameters:")
        parameter_data = {
            "Parameter": ["Active Instances", "Monitoring Services", "Response Time", "Resource Utilization",
                          "Service Availability", "Throughput", "Database Connections", "Network Traffic"],
            "Value": [active_instances, monitoring_services, f"{response_time:.2f} ms",
                      f"{resource_utilization:.2f}%", f"{service_availability:.2f}%",
                      f"{throughput:.2f} Mbps", db_connections, f"{network_traffic:.2f} GB"],
            "Status": ["✅"] * 8  # Green tick marks indicating system is active
        }
        parameter_table = st.table(pd.DataFrame(parameter_data).set_index('Parameter'))
        parameter_table.table_style = {"align": "center"}  # Center-align the content

    else:
        st.error(f"{system_name} is Offline")
        # Display parameters for offline systems with values indicating offline state
        st.write("Additional Parameters:")
        parameter_data = {
            "Parameter": ["Active Instances", "Monitoring Services", "Response Time", "Resource Utilization",
                          "Service Availability", "Throughput", "Database Connections", "Network Traffic"],
            "Value": [0] * 8,  # Setting all values to 0 for offline systems
            "Status": ["❌"] * 8  # Red cross marks indicating system is inactive
        }
        parameter_table = st.table(pd.DataFrame(parameter_data).set_index('Parameter'))
        parameter_table.table_style = {"align": "center"}  # Center-align the content

# Main function to create the dashboard
def main():
    st.markdown("<h1 style='text-align: center;'>Zelonia Cyberattack Simulation Dashboard</h1>", unsafe_allow_html=True)

    # Get admin controls from shared global variable
    admin_controls = get_admin_controls()
    # Get admin inputs from shared global variable
    admin_inputs = get_admin_inputs()

    # Sidebar for login
    login = st.sidebar.checkbox("Login as Admin")

    if login:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if username == 'admin' and password == 'password':
            st.sidebar.success("Logged in as Admin")
            admin_access = True
        else:
            st.sidebar.error("Invalid username or password")
            admin_access = False
    else:
        admin_access = False

    # Admin controls for the map
    if admin_access:
        st.sidebar.subheader("Admin Controls")
        st.sidebar.write("Map Controls:")
        for server in admin_inputs['num_affected_points']:
            admin_inputs['num_affected_points'][server] = st.sidebar.selectbox(f"{server} Status", ["Online", "Isolated", "Offline"])

        #admin_inputs["num_affected_points"] = st.sidebar.slider("Number of Affected Points", min_value=0, max_value=20, value=admin_inputs["num_affected_points"])

        admin_inputs['attack_server_found'] = st.sidebar.checkbox("Show attack server: ")

        # Admin controls for system status
        st.sidebar.write("System Status Controls:")
        for system_name in admin_controls:
            admin_controls[system_name] = st.sidebar.selectbox(f"{system_name} Status", ["Online", "Offline"])

        

    # Display the map
    st.subheader("Map of Affected Targets")
    st.write("Blinking red dots indicate attacked targets")
    st.markdown("### Please wait, loading map...")

    # Render the map based on admin input
    map_html = create_new_map(admin_inputs["num_affected_points"], admin_inputs['attack_server_found'])
    st.components.v1.html(map_html, height=1000)#, width=700, height=500)

    # Component tabs: Navigation, Weather, Email, HR, Finance, Pay
    system_tabs = ["Navigation", "Weather", "Email", "HR", "Finance", "Pay"]
    selected_tab = st.selectbox("Select System", system_tabs)
    display_system_health(selected_tab, admin_controls[selected_tab])
    
    if st.button("Scan the System"):
        my_bar_scan = st.progress(0, text='Scanning in progress...')
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar_scan.progress(percent_complete + 1, text='Scanning in progress...')
        time.sleep(1)
        my_bar_scan.empty()
        scanned_results = scan_file_storage(selected_tab, admin_controls[selected_tab])
            # Display pie charts for file extensions
        display_pie_charts(selected_tab, scanned_results)
        st.success("Scan complete!")

    
    

    # Display system health details for the selected tab
    if admin_access:
        system_name = selected_tab
        system_status = admin_controls[system_name]

    # Component: Navigation Data Integrity team member's device used by the hacker
    st.subheader("Navigation Data Integrity Team Member's Device")
    st.write("Device Status: Compromised")

# Run the dashboard
if __name__ == "__main__":
    main()