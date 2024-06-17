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
import math
import streamlit.components.v1 as components

BACKGROUND_COLOR = 'black'
COLOR = 'white'


st.set_page_config(
   page_title="Zelonia Technical Systems Dashboard",
   page_icon="data/Images/Zelonia Flag.jpg",
   layout="wide"
)



# Function to get admin controls
@st.cache_resource()
def get_admin_controls():
    return {
        "Navigation": "Online",
        "Weather": "Online",
        "Corporate": "Online"
    }

# Function to get admin inputs
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
@st.experimental_fragment
def scan_file_storage(system_name, status):
    # Simulate scanning process
    scanned_results = {}

    # Define file extension percentages for each system
    file_extensions = {
        "Navigation": {"shp": 56, "gpx": 21, "shx": 19, "geojson": 3, "csv": 1},
        "Weather": {"json": 40, "csv": 30, "txt": 20, "xml": 5, "grib": 3, "dat": 2},
        "Corporate": {"eml": 50, "pdf": 30, "xlsx": 10, "docx": 5, "csv": 3, "json": 2}
    }

    if status == "Online":
        # For online systems, return the predefined file extension percentages
        scanned_results = file_extensions.get(system_name, {})
        print(scanned_results)

    elif status == "Isolated":
        # For online systems, return the predefined file extension percentages
        scanned_results = {"Undefined":100}
        print(scanned_results)

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

def generate_points_around_coordinate(coordinate, num_points, max_offset_degrees):
    points = []
    for _ in range(num_points):
        lat = coordinate[0] + random.uniform(-max_offset_degrees, max_offset_degrees)
        lon = coordinate[1] + random.uniform(-max_offset_degrees, max_offset_degrees)
        points.append((lat, lon))
    return points

# Function to display pie charts for file extensions
def display_pie_charts(system_name, results):
    st.subheader(f"File Extensions for {system_name}")

    # Create a list of colors for the pie chart
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))


    # Create a Pie chart using Plotly
    fig = go.Figure(data=[go.Pie(labels=list(results.keys()), values=list(results.values()), textposition="inside", textinfo='label+percent', marker=dict(colors=colors))])
    
    
    # Render the Plotly chart
    st.plotly_chart(fig,use_container_width=True)

@st.experimental_fragment
def create_new_map(num_affected_points, show_attack_server):
    # Create a Folium map centered at Zelonia
    m = folium.Map(location=[1.3521+5, 103.8198+120], zoom_start=10, tiles='Cartodb dark_matter')

    # Add outline of Singapore as GeoJSON overlay
    folium.GeoJson(os.path.join("data/Geojsons", "Zelonia.geojson"), name="geojson").add_to(m)
    folium.GeoJson(os.path.join("data/Geojsons", "Putonia.geojson"), name="geojson2").add_to(m)

    servers=[ [[1.3521, 103.8198],
        [1.3578, 103.9870],
        [1.3196, 103.8253],
        [1.2901, 103.8029]
        ],
        [
        [1.2912, 103.8375],
        [1.3480, 103.6830],
        [1.3139, 103.7657],
        [1.2984, 103.7736],
        [1.3340, 103.7359]
        ],
        [
        [1.388307, 103.890594],
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
    headquarters = [ [1.257704+5, 103.675321+120],[1.399115+5, 103.814710+120],[1.356555+5, 103.901914+120]]
    
    keys = ["Navigation", "Weather", "Corporate"]

    for i in range(3):
        server_status = num_affected_points[keys[i]]
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
        else:
            hq = headquarters[i]
            folium.Marker(location=hq, icon=folium.Icon(icon='fa-building', prefix='fa',color='lightred', icon_color='black')).add_to(m)
            folium.CircleMarker(location=hq, radius=10, color='black', fill=True, fill_color='red', fill_opacity=0.8).add_to(m)
            for point in servers[i]:
                folium.CircleMarker(location=point, radius=4, color='black', fill=True, fill_color='red', fill_opacity=0.8).add_to(m)
                folium.PolyLine(locations=[point, hq], color='red', weight=1).add_to(m)

    if show_attack_server:
        folium.CircleMarker(location=[7.354704-60, 80.990871-100], radius=10, color='red', fill=True, fill_color='red').add_to(m)
        for i in range(2):
            folium.PolyLine(locations=[[7.354704-60, 80.990871-100], headquarters[i]], color='red', weight=2).add_to(m)


    # Add JavaScript for blinking effect
    script = """
    <script>
    setInterval(function() {
        var dots = document.querySelectorAll('.leaflet-interactive[fill-opacity="0.8"]');
        for (var i = 0; i < dots.length; i++) {
            dots[i].style.display = (dots[i].style.display === 'none' ? '' : 'none');
        }
    }, 1000);
    </script>
    """
    m.get_root().html.add_child(folium.Element(script))

    # Convert Folium map to HTML
    map_html = m._repr_html_()

    return map_html

@st.experimental_fragment
def create_device_map(num_affected_points, show_attack_server):
    # Create a Folium map centered at Zelonia
    m = folium.Map(location=[1.3521+5, 103.8198+120], zoom_start=10, tiles='Cartodb dark_matter')

    # Add outline of Singapore as GeoJSON overlay
    folium.GeoJson(os.path.join("data/Geojsons", "Zelonia.geojson"), name="geojson").add_to(m)
    folium.GeoJson(os.path.join("data/Geojsons", "Putonia.geojson"), name="geojson2").add_to(m)

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
    headquarters = [ [1.257704+5, 103.675321+120],[1.399115+5, 103.814710+120],[1.356555+5, 103.901914+120]]

    mobile_url = "data/Images/mobile-phone.png"
    comp_url = "data/Images/monitor.png"
    laptop_url = "data/Images/laptop.png"
    urls = [mobile_url, comp_url, laptop_url]
    i = 0
    keys = ["Navigation", "Weather", "Corporate"]


    for loc in headquarters:
        folium.Marker(location=loc, icon=folium.Icon(icon='fa-building', prefix='fa', color='green', icon_color='black')).add_to(m)
        points_around_coordinate = generate_points_around_coordinate(loc, random.randint(4,8),random.uniform(0.02,0.05))

        server_status = num_affected_points[keys[i]]
        i += 1

        if server_status == 'Online':
            folium.Marker(location=loc, icon=folium.Icon(icon='fa-building', prefix='fa', color='lightgreen', icon_color='black')).add_to(m)
            folium.Circle(location=loc, radius=random.randint(5000,8000), color='lightgreen', fill=True, fill_color='darkgreen', fill_opacity=0.5).add_to(m)
            for points in points_around_coordinate:
                icon = folium.CustomIcon(
                        random.choice(urls),
                        icon_size=(20, 20)
                    )

                folium.Marker(location=points, icon=icon).add_to(m)#folium.Icon(icon='fa-building', prefix='fa', color='red', icon_color='black')).add_to(m)
        elif server_status == 'Isolated':
            folium.Marker(location=loc, icon=folium.Icon(icon='fa-building', prefix='fa', color='lightgray', icon_color='black')).add_to(m)

        elif server_status == 'Offline':
            folium.Marker(location=loc, icon=folium.Icon(icon='fa-building', prefix='fa', color='black', icon_color='white')).add_to(m)
            folium.Circle(location=loc, radius=random.randint(5000,8000), color='black', fill=True, fill_color='red', fill_opacity=0.5).add_to(m)
            for points in points_around_coordinate:
                icon = folium.CustomIcon(
                        random.choice(urls),
                        icon_size=(20, 20)
                    )

                folium.Marker(location=points, icon=icon).add_to(m)#folium.Icon(icon='fa-building', prefix='fa', color='red', icon_color='black')).add_to(m)


    if show_attack_server:
        folium.CircleMarker(location=[7.354704-60, 80.990871-100], radius=10, color='red', fill=True, fill_color='red').add_to(m)
        folium.PolyLine(locations=[[7.354704-60, 80.990871-100], [1.406666+5, 103.769391+120]], color='red', weight=2).add_to(m)
        icon = folium.CustomIcon(
                    "data/Images/virus.png",
                    icon_size=(35, 35)
                )
        folium.Marker(location=[1.406666+5, 103.769391+120], icon=icon).add_to(m)
        for point in headquarters[:2]:
            folium.PolyLine(locations=[point, [1.406666+5, 103.769391+120]], color='red', weight=2,dash_array='10').add_to(m)


    # Add JavaScript for blinking effect
    script = """
    <script>
    setInterval(function() {
        var dots = document.querySelectorAll('.leaflet-interactive[fill-opacity="0.5"]');
        for (var i = 0; i < dots.length; i++) {
            dots[i].style.display = (dots[i].style.display === 'none' ? '' : 'none');
        }
    }, 1000);
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
        resource_utilization = random.uniform(60, 80)  # Random resource utilization (60% to 80%)
        service_availability = random.uniform(99.5, 99.9)  # Random service availability (99.5% to 99.9%)

        # Display additional parameters in a table format
        st.write("Additional Parameters:")
        parameter_data = {
            "Parameter": ["Active Instances", "Resource Utilization",
                          "Service Availability"],
            "Value": [active_instances,
                      f"{resource_utilization:.2f}%", f"{service_availability:.2f}%"],
            "Status": ["✅"] * 3  # Green tick marks indicating system is active
        }
        parameter_table = st.dataframe(pd.DataFrame(parameter_data).set_index('Parameter'),use_container_width=True)
        parameter_table.table_style = {"align": "center"}  # Center-align the content
    
    elif system_status == "Isolated":
        st.warning(f"{system_name} is Rebooting",icon="⚠️")
        st.write("System Health: N/A")
        system_health = 0  # Random system health value (96 to 100)
        my_bar = st.progress(0)

        for percent_complete in range(system_health):
            time.sleep(0.02)
            my_bar.progress(percent_complete + 1)

        st.write("Additional Parameters:")
        parameter_data = {
            "Parameter": ["Active Instances", "Resource Utilization",
                        "Service Availability"],
            "Value": ['N/A'] * 3,  # Setting all values to N/A
            "Status": ["⌛"] * 3 
        }
        parameter_table = st.dataframe(pd.DataFrame(parameter_data).set_index('Parameter'),use_container_width=True)
        parameter_table.table_style = {"align": "center"}  # Center-align the content




    else:
        st.error(f"{system_name} is Offline")
        system_health = random.randint(0,2)  # Random system health value (96 to 100)
        st.write(f"System Health: {system_health}%")
        my_bar = st.progress(0)
        for percent_complete in range(system_health):
            time.sleep(0.02)
            my_bar.progress(percent_complete + 1)
        # Display parameters for offline systems with values indicating offline state
        st.write("Additional Parameters:")
        parameter_data = {
            "Parameter": ["Active Instances", "Resource Utilization",
                          "Service Availability"],
            "Value": [0] * 3,  # Setting all values to 0 for offline systems
            "Status": ["❌"] * 3  # Red cross marks indicating system is inactive
        }
        parameter_table = st.dataframe(pd.DataFrame(parameter_data).set_index('Parameter'),use_container_width=True)
        parameter_table.table_style = {"align": "center"}  # Center-align the content

# Main function to create the dashboard
def main():
    st.markdown("<h1 style='text-align: center;'>Zelonia Technical Systems Dashboard</h1>", unsafe_allow_html=True)

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
        # Admin controls for system status
        st.sidebar.write("System Status Controls:")
        for system_name in admin_controls:
            admin_controls[system_name] = st.sidebar.selectbox(f"{system_name} Status", ["Online", "Isolated", "Offline"])

        
        admin_inputs['attack_server_found'] = st.sidebar.checkbox("Show attack server: ")

        
        
    map_html = create_new_map(admin_controls, admin_inputs['attack_server_found'])
    # Display the map
    col1,col2 = st.columns(2)

    device_map = create_device_map(admin_controls, admin_inputs['attack_server_found'])


    with col1:
        with st.container( border=True):
            st.markdown("<h2 style='text-align: center;'>Technical Systems Servers</h2>", unsafe_allow_html=True)
            #st.subheader("Technical Systems Servers", divider="blue")
            #st.write("Blinking red dots indicate attacked targets")
            # Render the map based on admin input
            components.html(map_html, height=400)

    
    with col2:
        with st.container( border=True):
            st.markdown("<h2 style='text-align: center;'>Connected Devices</h2>", unsafe_allow_html=True)
            #st.subheader("Connected Devices", divider="orange")
            #st.write("Devices connected to different servers")
            # Render the map based on admin input
            components.html(device_map, height=400)

    
    sys_col1, sys_col2, sys_col3 = st.columns(3)
    system_tabs = ["Navigation", "Weather", "Corporate"]

    with sys_col1:
        with st.container( border=True):
            selected_tab = system_tabs[0]
            display_system_health(selected_tab, admin_controls[selected_tab])
            scanned_results = scan_file_storage(selected_tab, admin_controls[selected_tab])
            display_pie_charts(selected_tab, scanned_results)

    with sys_col2:
        with st.container( border=True):
            selected_tab = system_tabs[1]
            display_system_health(selected_tab, admin_controls[selected_tab])
            scanned_results = scan_file_storage(selected_tab, admin_controls[selected_tab])
            display_pie_charts(selected_tab, scanned_results)

    with sys_col3:
        with st.container( border=True):
            selected_tab = system_tabs[2]
            display_system_health(selected_tab, admin_controls[selected_tab])
            scanned_results = scan_file_storage(selected_tab, admin_controls[selected_tab])
            display_pie_charts(selected_tab, scanned_results)


# Run the dashboard
if __name__ == "__main__":
    main()
