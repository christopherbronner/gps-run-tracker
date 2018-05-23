import pandas as pd
import gpxpy
import gpxpy.gpx
import geopy.distance
from time import strftime
from time import strptime

# Loads gpx file and returns data frame run
def load_run_to_df(filename): 
    
    # Load file into run_data using gpxpy
    with open(filename) as f:
        run_data = gpxpy.parse(f)
    f.closed
    
    # Initialize DataFrames
    df_dict = {'time': [],'lat': [],'lon': [],'elev': []}
    df = pd.DataFrame(df_dict)
    
    
    # Create DataFrame containing time, latitude, longitude, elevation columns
    for track in run_data.tracks:
        for segment in track.segments:
            for point in segment.points:
                df_newRow = pd.DataFrame([[point.time, point.latitude, point.longitude, point.elevation]], columns=['time','lat','lon','elev'])
                df = df.append(df_newRow, ignore_index=True)
                
    # Create additional column for accumulative distance
    tmp = [0]
    for i, row in df[1:].iterrows():
        prevCoord = (df.iloc[i-1]['lat'],df.iloc[i-1]['lon'])
        currCoord = (df.iloc[i]['lat'],df.iloc[i]['lon'])
        tmp.append(tmp[-1] + geopy.distance.vincenty(prevCoord, currCoord).mi)
    df['accuDist']=tmp
    
    return df


def strfdelta(tdelta): # Reformats timedelta object to h:mm:ss
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    formatted = str(d['hours']).zfill(2) +':'+ str(d['minutes']).zfill(2) +':'+ str(d['seconds']).zfill(2)
    return formatted

def file_name_from_path(path): # returns file name from file path
    file_name = ''
    for i in path:
        file_name += i
        if i=='/':
            file_name = ''
    return file_name



def evaluate_file(filename):
    df = load_run_to_df(filename) # Load file into dataframe using load_run_to_df
    
    total_distance = df.iloc[-1]['accuDist'] # Extract total distance
    
    # Extract start time (is <class 'pandas._libs.tslib.Timestamp'>)
    start_time = df.iloc[0]['time']
    
    # Calculate total time of this run
    total_time_obj = df.iloc[-1]['time']-df.iloc[0]['time'] # creates timedelta object
    total_time_formatted = strfdelta(total_time_obj)
    
    # Calculate average pace
    avg_pace = total_time_obj.seconds / (total_distance*60)
    
    # Calculate total climb
    total_climb=0
    for i, row in df[1:].iterrows():
        height_difference = 3.28084*(df.iloc[i]['elev'] - df.iloc[i-1]['elev'])
        if height_difference>0:
            total_climb += height_difference


    # Return the various statistics about this run
    stats = [file_name_from_path(filename), start_time, total_distance, total_time_formatted, avg_pace, total_climb]
    return stats