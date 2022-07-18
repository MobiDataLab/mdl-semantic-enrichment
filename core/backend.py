import geopandas as gpd
import shapely
import pandas as pd
import numpy as np
import skmob
from skmob.preprocessing import filtering
from skmob.preprocessing import detection
from skmob.preprocessing import compression
from ptrail.core.TrajectoryDF import PTRAILDataFrame
from ptrail.features.kinematic_features import KinematicFeatures as spatial
import pickle
from sklearn.preprocessing import StandardScaler
import geohash2
import osmnx as ox
from core.RDF_builder import RDFBuilder

shapely.speedups.disable()

class demo():

    '''
    Class `demo` is a super class containing one subclass per module (in our case `preprocessing`, `segmentation`, `enrichment`)
    '''

    def __init__(self):
        '''
        Initialize `subclasses` that is a list of all subclasses
        '''
        subclasses = self.__subclasses__()

class Preprocessing(demo):
    '''
    `preprocessing` module
    '''
    pass

class Segmentation(demo):
    '''
    `segmentation` module
    '''
    pass

class Enrichment(demo):

    '''
    `enrichment` module
    '''
    pass


class preprocessing1(Preprocessing):
    '''
    `preprocessing1` is a subclass of `Preprocessing` to preprocess trajectories and allows users to:
    1) remove trajectories with a few number of points
    2) remove outliers
    3) compress trajectories
    '''
    

    ### STATIC VARIABLES ###
    
    df = gpd.GeoDataFrame()



    ### CLASS CONSTRUCTOR ###
    def __init__(self, list_):

        self.path = list_[0]
        self.kmh = list_[1]
        self.num_point = list_[2]



    ### CLASS METHODS ###
    
    def core(self):
                
        if self.path[-3:] == 'csv':
            gdf = pd.read_csv(self.path)
        elif self.path[-7:] == 'parquet':
            gdf = pd.read_parquet(self.path)
        else:
            return 'Fail in uploading file'

        # ## PREPROCESSING

        # eliminate trajectories with a number of points lower than num_point
        grouped = gdf.groupby('traj_id')
        gdf = grouped.filter(lambda x: len(x) >= self.num_point)

        # convert GeoDataFrame into pandas DataFrame
        df = pd.DataFrame(gdf)
        # now create a TrajDataFrame from the pandas DataFrame
        tdf = skmob.TrajDataFrame(df, latitude='lat', longitude='lon', datetime='time', user_id='user',
                                  trajectory_id='traj_id')
        ftdf = filtering.filter(tdf, max_speed_kmh=self.kmh)
        ctdf = compression.compress(ftdf, spatial_radius_km = 0.2)

        self.df = ctdf
        return ''

    def get_num_users(self):

        return str(len(self.df.uid.unique()))

    def get_num_trajs(self):

        return str(len(self.df.tid.unique()))

    def output(self):

        self.df.to_parquet('data/temp_dataset/traj_cleaned.parquet')



'''class preprocessing2(Preprocessing):
    """
    `preprocessing2` is a subclass of `Preprocessing` to preprocess trajectories and allows users to:
    1) remove outliers
    2) compress trajectories
    """
    pass

    df = gpd.GeoDataFrame()

    def __init__(self,list_):

        self.path = list_[0]
        self.kmh = list_[1]

    def core(self):

        if self.path[-3:] == 'csv':
            df = pd.read_csv(self.path)
        elif self.path[-7:] == 'parquet':
            df = pd.read_parquet(self.path)
        else:
            return 'Fail in uploading file'

        # ## PREPROCESSING

        # create a TrajDataFrame from the pandas DataFrame
        tdf = skmob.TrajDataFrame(df, latitude='lat', longitude='lon', datetime='time', user_id='user',
                                  trajectory_id='traj_id')
        ftdf = filtering.filter(tdf, max_speed_kmh=self.kmh)
        ctdf = compression.compress(ftdf, spatial_radius_km=0.2)

        self.df = ctdf
        return ''

    def get_num_users(self):

        return str(len(self.df.uid.unique()))

    def get_num_trajs(self):

        return str(len(self.df.tid.unique()))

    def output(self):

        self.df.to_parquet('data/temp_dataset/traj_cleaned.parquet')

'''


class stops_and_moves(Segmentation):

    '''
    `stops_and_moves` is a subclass of `Segmentation` to detect stop points and moves.
    '''

    stops = pd.DataFrame()
    moves = pd.DataFrame()
    preprocessed_trajs = pd.DataFrame()

    def __init__(self, list_):
        
        self.minutes = list_[0]
        self.radius = list_[1]
        self.preprocessed_trajs = pd.read_parquet('data/temp_dataset/traj_cleaned.parquet')



    def core(self):
        
        # read preprocessed dataframe
        tdf = skmob.TrajDataFrame(self.preprocessed_trajs)

        # stop detection
        stdf = detection.stops(tdf, stop_radius_factor=0.5, minutes_for_a_stop=self.minutes, spatial_radius_km=self.radius, leaving_time=True)
        self.stops = stdf
        # save stops
        stdf.to_parquet('data/temp_dataset/stops.parquet')

        # move detection
        trajs = tdf.copy()
        starts = stdf.copy()
        ends = stdf.copy()

        trajs.set_index(['tid','datetime'],inplace=True)
        starts.set_index(['tid','datetime'],inplace=True)
        ends.set_index(['tid','leaving_datetime'],inplace=True)

        traj_ids = trajs.index
        start_ids = starts.index
        end_ids = ends.index

        # some datetime into stdf are approximated. In order to retrieve moves, we have to check the exact datime into 
        # trajectory dataframe
        # we use `isin()` method to reduce time computation
        traj_df = pd.DataFrame(traj_ids, columns=['trajs'])
        start_df = pd.DataFrame(start_ids, columns=['start'])
        end_df = pd.DataFrame(end_ids, columns=['end'])

        start_df['is_in_traj'] = start_df['start'].isin(traj_df['trajs'])
        end_df['is_in_traj'] = end_df['end'].isin(traj_df['trajs'])

        start_df['end'] = end_df['end']
        start_df['is_in_traj_end'] = end_df['is_in_traj']

        # remove stops which aren't into tdf
        start_df = start_df[(start_df['is_in_traj']!=False)|(start_df['is_in_traj_end']!=False)]

        # save index of incomplete stops and convert them into MultiIndex
        incomplete_end = start_df['end'][(start_df['is_in_traj']==False)&(start_df['is_in_traj_end']==True)] 
        incomplete_start = start_df['start'][(start_df['is_in_traj']==True)&(start_df['is_in_traj_end']==False)]

        if not incomplete_end.empty:
            incomplete_end = pd.MultiIndex.from_tuples(incomplete_end)

        if not incomplete_start.empty:
            incomplete_start = pd.MultiIndex.from_tuples(incomplete_start)

        # save complete index
        start_df = start_df[(start_df['is_in_traj']==True)&(start_df['is_in_traj_end']==True)] 
        
        new_start = pd.MultiIndex.from_tuples(start_df['start'])
        new_end = pd.MultiIndex.from_tuples(start_df['end'])
        new_start.set_names(['tid','datetime'],inplace=True)
        new_end.set_names(['tid','datetime'],inplace=True)
        
        # set start and end of stops (using two columns in order to avoid overlaps)
        trajs['start_stop'] = np.nan
        trajs['start_stop'].loc[new_start] = 1
        trajs['end_stop'] = np.nan
        trajs['end_stop'].loc[new_end] = 1  

        trajs.reset_index(inplace=True)
        start_idx = trajs[trajs['start_stop']==1].index.to_list()
        end_idx = trajs[trajs['end_stop']==1].index.to_list()

        # set incomplete index
        starts_ = [traj_ids.get_loc(e).start - 1 for e in incomplete_end]
        ends_ = [traj_ids.get_loc(s).start + 1 for s in incomplete_start]

        if starts_ != []:
            start_idx = start_idx + starts_
    
        if ends_ != []:
            end_idx = end_idx + ends_

        trajs['move_id'] = np.nan
        
        i = 1
        for s,e in zip(start_idx,end_idx):
            trajs['move_id'][s:e+1] = i
            i += 1

        trajs['move_id'].ffill(inplace=True)
        trajs['move_id'].fillna(0,inplace=True)

        trajs['move_id'][(trajs['start_stop']==1)|(trajs['end_stop']==1)] = -1

        moves = trajs[trajs['move_id']!=-1]
        self.moves = moves.copy()
        moves.to_parquet('data/temp_dataset/moves.parquet')

        del end_df, start_df, traj_df

    def get_users(self):
        
        return self.moves['uid'].unique()

    def get_trajectories(self, uid):

        return len(self.moves[self.moves['uid']==uid]['tid'].unique())

    def get_stops(self, uid):

        return len(self.stops[self.stops['uid']==uid])

    def get_duration(self, uid):

        s = self.stops[self.stops['uid']==uid]
        s['duration'] = (s['leaving_datetime'] - s['datetime']).astype('timedelta64[m]')

        return round(s['duration'].mean(),2)



class stop_move_enrichment(Enrichment):

    '''
    `stop_move_enrichment` is a subclass of `Enrichment` module. This subclass allows users to:
    1) enrich moves with transportation mean
    2) enrich stops labeling them as occasional and systematic ones
        2.a) occasional stops are enriched with PoIs, weather, etc.
        2.b) systematic stops are enriched as home/work or other
    '''


    ### CLASS CONSTRUCTOR ###

    def __init__(self,list_):
    
        ### Reset the state of the static variables...
        self.stops = pd.DataFrame()
        self.moves = pd.DataFrame()
        self.mats = gpd.GeoDataFrame()
        
    
        print("Executing the constructor of the semantic enrichment module...")
        print(f"Values of the list passed to the constructor: {list_}")

        if list_[0] == 'yes':
            self.enrich_moves = True
            self.moves = pd.read_parquet('data/temp_dataset/moves.parquet')
        else:
            self.enrich_moves = False

        self.place = list_[1]

        if list_[2] == ['no']:
            self.list_pois = []
        else:
            self.list_pois = list_[2]

        if list_[3] == 'no':
            self.upload_stops = 'no'
        else:
            self.upload_stops = list_[3]

        self.semantic_granularity = list_[4]
        self.max_distance = list_[5]

        # Variabili gestione arricchimento social media post.
        if list_[6] == 'no':
            self.tweet_user = False
        else:
            self.tweet_user = True

        if list_[7] == 'no':
            self.upload_users = 'no'
        else:
            self.upload_users = list_[7]

        # Variabili gestione arricchimento social media post.
        if list_[8] == 'no':
            self.weather = False
        else:
            self.weather = True

        if list_[9] == 'no':
            self.upload_trajs = 'no'
        else:
            self.upload_trajs = list_[9]
        
        # Variabili gestione scrittura grafo RDF.
        if list_[-1] == 'yes':
            self.rdf = 'yes'
        else:
            self.rdf = 'no'



    ### CLASS PUBLIC METHODS ###

    def core(self):
    
        print("Executing the core of the semantic enrichment module...")
    


        #################################
        ### ---- MOVE ENRICHMENT ---- ###
        #################################

        moves = self.moves
        if self.enrich_moves == True:
            print("Executing move enrichment...")
            
            # add speed, acceleration, distance info using PTRAIL
            df = PTRAILDataFrame(moves, latitude='lat', longitude='lng', datetime='datetime', traj_id='tid')
            speed = spatial.create_speed_column(df)
            bearing = spatial.create_bearing_rate_column(speed)
            acceleration = spatial.create_jerk_column(bearing)

            # save acceleration
        
            # load random forest classifier
            model = pickle.load(open('models/best_rf.sav', 'rb'))

            # preparing input for transport mode detection
            acceleration.reset_index(inplace=True)
            acceleration.set_index(['traj_id','move_id'],inplace=True)

            acceleration2 = acceleration.copy()

            acceleration['tot_distance'] = acceleration.groupby(['traj_id','move_id']).apply(lambda x: x['Distance'].sum())
            acceleration = acceleration.groupby(['traj_id','move_id']).mean()
            acceleration[['max_bearing','max_bearing_rate','max_speed','max_acceleration','max_jerk']] = acceleration2.groupby(['traj_id','move_id']).apply(lambda x: x[['Bearing', 'Bearing_Rate', 'Speed', 'Acceleration', 'Jerk']].max())

            col_to_train = ['Bearing', 'Bearing_Rate', 'Speed', 'Acceleration', 'Jerk','tot_distance','max_bearing','max_bearing_rate','max_speed','max_acceleration','max_jerk']
            col = acceleration.columns.to_list()
            col_to_drop = [c for c in col if c not in col_to_train]
            acceleration.drop(columns=col_to_drop, inplace=True)
            acceleration.fillna(0,inplace=True)

            scaler = StandardScaler()
            scaled = scaler.fit_transform(acceleration)

            transport_pred = model.predict(scaled)
            acceleration['label'] = transport_pred

            # transport label:
            # 0: walk
            # 1: bike
            # 2: bus
            # 3: car
            # 4: subway
            # 5: train
            # 6: taxi

            moves.set_index(['tid','move_id'],inplace=True)
            moves_index = moves.index
            acceleration_index = acceleration.index
            moves.loc[moves_index.isin(acceleration_index),'label'] = acceleration.loc[acceleration_index.isin(moves_index),'label']
            
            self.moves = moves
            moves.to_parquet('data/enriched_moves.parquet')



        ############################################
        ### ---- SYSTEMATIC STOP ENRICHMENT ---- ###
        ############################################
        
        print("Executing systematic stop enrichment...")

        self.stops = pd.read_parquet('data/temp_dataset/stops.parquet')

        stops = self.stops.copy()
        stops.reset_index(inplace=True)
        stops.rename(columns={'index':'stop_id'},inplace=True)
        stops['pos_hashed'] = stops[['lat','lng']].apply(lambda x: geohash2.encode(x[0],x[1],7),raw=True,axis=1)
        stops['frequency'] = 0

        def compute_freq(x):
            freqs = x.groupby('pos_hashed').count()['frequency']
            return freqs

        systematic_sp = pd.DataFrame(stops.groupby('uid').apply(lambda x: compute_freq(x)))
        sp = stops.copy()
        sp.set_index(['uid','pos_hashed'],inplace=True)
        sp['frequency'] = systematic_sp['frequency']
        sp.reset_index(inplace=True)
        systematic_stops = sp[sp['frequency'] > 2]
        
        # 1 - case where systematic stops have been found...
        if(systematic_stops.shape[0] != 0) :
            systematic_stops['start_time'] = systematic_stops['datetime'].dt.hour
            systematic_stops['end_time'] = systematic_stops['leaving_datetime'].dt.hour
            systematic_stops.reset_index(inplace=True,drop=True)

            #global freq
            freq = pd.DataFrame(np.zeros((len(systematic_stops),24)))
            freq['uid'] = systematic_stops['uid']
            freq['location'] = systematic_stops['pos_hashed']
            freq.drop_duplicates(['uid','location'],inplace=True)

            def update_hour(x):
                
                start_col = x[-2]
                end_col = x[-1]
                
                start_raw = freq[(freq['uid']==x[0])&(freq['location']==x[1])].first_valid_index()
                if start_raw != None:
                    end_raw = start_raw+1
                    
                    if start_col<end_col:
                        
                        freq.loc[start_raw:end_raw,start_col:end_col] += 1
                    
                    elif start_col==end_col:
                        
                        freq.loc[start_raw:end_raw,start_col] += 1
                        
                    else:
                        
                        freq.loc[start_raw:end_raw,start_col:23] += 1
                        freq.loc[start_raw:end_raw,0:end_col] += 1

            systematic_stops.apply(lambda x: update_hour(x),raw=True,axis=1)

            hours = [i for i in range(0,24)]
            freq['sum'] = freq[hours].sum(axis=1)
            freq['tot'] = freq.groupby('uid')['sum'].sum()
            freq['importance'] = freq['sum'] / freq['tot']

            freq.set_index(['uid','location'],inplace=True)
            freq.drop(columns=['sum','tot'],inplace=True)

            freq['night'] = freq[[23,0,1,2,3,4,5]].sum(axis=1)
            freq['morning'] = freq[[6,7,8,9,10,11,12]].sum(axis=1)
            freq['afternoon'] = freq[[13,14,15,16,17,18]].sum(axis=1)
            freq['evening'] = freq[[19,20,21,22]].sum(axis=1)

            largest = pd.DataFrame(freq.groupby('uid')['importance'].nlargest(2))
            largest_index = largest.index.droplevel(0)
            freq['home'] = 0
            freq['work'] = 0
            freq['other'] = 0

            w_home = [0.6,0.1,0.1,0.4]
            w_work = [0.1,0.6,0.4,0.1]
        
            freq['p_home'] = (freq[['night','morning','afternoon','evening']].loc[largest_index] * w_home).sum(axis=1)
            freq['p_work'] = (freq[['night','morning','afternoon','evening']].loc[largest_index] * w_work).sum(axis=1)
            freq['home'] = freq['p_home'] / freq[['p_home','p_work']].sum(axis=1)
            freq['work'] = freq['p_work'] / freq[['p_home','p_work']].sum(axis=1)
            freq['other'].loc[~freq.index.isin(largest_index)] = 1
            freq['home'].fillna(0,inplace=True)
            freq['work'].fillna(0,inplace=True)

            systematic_stops.set_index(['uid','pos_hashed'],inplace=True)
            systematic_stops['home'] = 0
            systematic_stops['work'] = 0
            systematic_stops['other'] = 0
            systematic_stops['home'].loc[systematic_stops.index.isin(freq.index)] = freq['home'].loc[freq.index.isin(systematic_stops.index)]
            systematic_stops['work'].loc[systematic_stops.index.isin(freq.index)] = freq['work'].loc[freq.index.isin(systematic_stops.index)]
            systematic_stops['other'].loc[systematic_stops.index.isin(freq.index)] = freq['other'].loc[freq.index.isin(systematic_stops.index)]
            systematic_stops.reset_index(inplace=True)
            
        # 2 - case where no systematic stops have been found...adapt the empty dataframe
        #     for the code that will use it.
        else :
            new_cols = ['home', 'work', 'other', 'start_time', 'end_time']
            systematic_stops = systematic_stops.reindex(systematic_stops.columns.union(new_cols), axis=1)
            
        # Write out the dataframe...
        self.systematic = systematic_stops
        self.systematic.to_parquet('data/systematic_stops.parquet')
        
        
        
        ############################################
        ### ---- OCCASIONAL STOP ENRICHMENT ---- ###
        ############################################

        def select_columns(gdf, threshold=80.0):
            """
            A function to select columns of a GeoDataFrame that have a percentage of null values
            lower than a given threshold.
            Returns a GeoDataFrame

            -----------------------------
            gdf: a GeoDataFrame

            threshold: default 80.0
                a float representing the maxium percentage of null values in a column.
            """
            
            # list of columns
            cols = gdf.columns
            # print(f"Initial set of POI columns...{cols}")
            
            # list of columns to delete
            del_cols = []
            for c in cols:

                # check if column contains only null value
                if(gdf[c].isnull().all()):
                    # save the empty column
                    del_cols.append(c)
                    continue

                # control only columns with at least one null value
                if(gdf[c].isnull().any()):

                    # compute number of null values
                    null_vals = gdf[c].isnull().value_counts()[1]
                    # compute percentage w.r.t. total number of sample
                    perc = null_vals/len(gdf[c])*100

                    # save only columns that have a perc of null values lower than the given threshold
                    if(threshold <= perc):
                        del_cols.append(c)

        
            # Now, drop the selected columns MINUS 'osmid' and 'wikidata' 
            del_cols = list(set(del_cols) - set(['osmid', 'wikidata']))
            gdf = gdf.drop(columns = del_cols)

            # print(f"POI dataframe info: {gdf.info()}")
            return gdf



        def preparing_stops(stop,max_distance):
    
            # buffer stop points -> convert their geometries from points into polygon 
            # (we set the radius of polygon = to the radius of sjoin) 
            stops = gpd.GeoDataFrame(stop, geometry=gpd.points_from_xy(stop.lng, stop.lat))
            stops.set_crs('epsg:4326',inplace=True)
            stops.to_crs('epsg:3857',inplace=True)
            stops['geometry_stop'] = stops['geometry']
            stops['geometry'] = stops['geometry_stop'].buffer(max_distance)

            return stops



        def semantic_enrichment(stop, semantic_df, suffix):
        
            #print("DEBUG enrichment occasional stops...")
            
            # duplicate geometry column because we loose it during the sjoin_nearest
            s_df = semantic_df.copy()
            s_df['geometry_'+suffix] = s_df['geometry']
            s_df['osmid'] = s_df['osmid'].astype(str)
            
            #print(f"Stampa df stop occasionali: {stop.info()}")
            #print(f"Stampa df POIs: {s_df.info()}")
            
            # now we can use sjoin_nearest to obtain the results we want
            mats = stop.sjoin_nearest(s_df, max_distance=0.00001, how='left', rsuffix=suffix)
            
            # compute the distance between the stop point and the POI geometry
            #mats['distance_'+suffix] = mats['geometry_stop'].distance(mats['geometry_'+suffix])
            mats['distance'] = mats['geometry_stop'].distance(mats['geometry_'+suffix])
            
            # sort by distance
            #mats = mats.sort_values(['stop_id','distance_'+suffix])
            mats = mats.sort_values(['tid','stop_id','distance'])
            
            #print(f"Stampa df risultati: {mats.info()}")
            return mats



        def download_poi_osm(list_pois, place, semantic_granularity) :
        
            # Here we download the POIs from OSM if the list of types of POIs is not empty.
            gdf_ = gpd.GeoDataFrame()
            if list_pois != [] :
            
                for key in list_pois:

                    # downloading POI
                    print(f"Downloading {key} POIs from OSM...")
                    poi = ox.geometries_from_place(place, tags={key:True})
                    print(f"Download completed! Dataframe with the downloaded POIs: {poi}")
                    
                    # Immediately return the empty dataframe if it doesn't contain any suitable POI...
                    if poi.empty : 
                        print("No POI found...")
                        new_cols = ['osmid', 'wikidata', 'geometry', 'category']
                        poi = poi.reindex(poi.columns.union(new_cols), axis=1)
                        return poi
                    
                    
                    # convert list into string in order to save poi into parquet
                    if 'nodes' in poi.columns:
                        poi['nodes'] = poi['nodes'].astype(str)

                    if 'ways' in poi.columns:
                        poi['ways'] = poi['ways'].astype(str)

                    poi.reset_index(inplace=True)
                    poi.rename(columns={key: 'category'}, inplace=True)
                    poi['category'].replace({'yes': key}, inplace=True)

                    if poi.crs is None:
                        poi.set_crs('epsg:4326',inplace=True)
                        poi.to_crs('epsg:3857',inplace=True)
                    else:
                        poi.to_crs('epsg:3857',inplace=True)
                    
                    # Now drop the columns with too many missing values...
                    poi = select_columns(poi, semantic_granularity)
                    
                    # Now write out this subset of POIs to a file. 
                    poi.to_parquet('data/poi/' + key + '.parquet')

                    # And finally, concatenate this subset of POIs to the other POIs
                    # that have been added to the main dataframe so far.
                    gdf_ = pd.concat([gdf_, poi])
            
            
                # print(f"A few info on the POIs downloaded from OSM: {gdf_.info()}")
                gdf_.to_parquet('data/poi/pois.parquet')
                return gdf_



        print("Executing occasional stop enrichment...")

        occasional_stops = stops[~stops['stop_id'].isin(systematic_stops['stop_id'])]
        self.occasional = occasional_stops
        

        # Get a POI dataset, either from OSM or from a file. 
        gdf_ = None
        if self.upload_stops == 'no' :
            print(f"Downloading POIs from OSM for the location of {self.place}. Selected types of POIs: {self.list_pois}")
            gdf_ = download_poi_osm(self.list_pois, self.place, self.semantic_granularity)
        else :    
            print(f"Using a POI file: {self.upload_stops}!")
            gdf_ = gpd.read_parquet(self.upload_stops)

            if gdf_.crs is None:
                gdf_.set_crs('epsg:4326', inplace=True)
                gdf_.to_crs('epsg:3857', inplace=True)
            else:
                gdf_.to_crs('epsg:3857', inplace=True)
        print(f"A few info on the POIs that will be used to enrich the occasional stops: {gdf_.info()}")


        # Calling functions internal to this method...
        o_stops = preparing_stops(occasional_stops, self.max_distance)    
        mat = semantic_enrichment(o_stops, gdf_[['osmid','wikidata','geometry','category']], 'poi')

        ######## PROVA ###########
        #mat.set_index(['stop_id','lat','lng'],inplace=True)
        self.mats = mat.copy()
        self.mats.to_parquet('data/enriched_occasional.parquet')
        
        
        
        ####################################
        ### ---- WEATHER ENRICHMENT ---- ###
        ####################################       

        def move_weather_enrichment(moves, weather) :        

            res = moves.copy()
            if weather is not None :
                
                res['DATE'] = (res['datetime'].dt.date).astype(str)
                res = res.merge(weather, on = 'DATE', how = 'left')
                res.drop(columns = ['DATE'])
                res.rename(columns = {'TAVG_C' : 'temperature', 'DESCRIPTION' : 'w_conditions'}, inplace = True)
                
                # The merge has eliminated the old multilevel index on moves...let's restore it. 
                res = res.set_index(moves.index) 

            # If weather conditions are not available then set NA values in the appropriate columns.
            else :
                res['temperature'] = pd.NA
                res['w_conditions'] = pd.NA

            return(res)
        
        
        def weather_enrichment(traj_cleaned, weather) :
            
            traj_cleaned['DATE'] = (traj_cleaned['datetime'].dt.date).astype(str)
            
            # Per ogni traiettoria, trova il primo ed ultimo sample in ogni giornata coperta dalla traiettoria.
            gb = traj_cleaned.groupby(['tid', 'DATE'])
            traj_day = gb.first().reset_index()
            end_traj_day = gb.last().reset_index()

            # Adesso joina i due dataframe.
            traj_day['end_lat'] = end_traj_day['lat']
            traj_day['end_lng'] = end_traj_day['lng']
            traj_day['end_datetime'] = end_traj_day['datetime']
            print(traj_day)
            print(traj_day.info())
            
            # For each trajectory and day covered by the trajectory, find whether we can associate weather information.
            weather_enrichment = traj_day.merge(weather, on = 'DATE', how = 'inner')

            weather_enrichment['datetime'] = pd.to_datetime(weather_enrichment['datetime'], utc = True)
            weather_enrichment['end_datetime'] = pd.to_datetime(weather_enrichment['end_datetime'], utc = True)

            print(weather_enrichment)
            print(weather_enrichment.info())

            return(weather_enrichment)
        
            
            
        df_weather_enrichment = None
        print(f"Valore self.weather: {self.weather}")
        if self.weather :
            print("Adding weather info to the trajectories...")

            traj_cleaned = pd.read_parquet('./data/temp_dataset/traj_cleaned.parquet')
            weather = pd.read_parquet(self.upload_trajs)
            
            df_weather_enrichment = weather_enrichment(traj_cleaned, weather)
            df_weather_enrichment.to_parquet('./data/weather_enrichment.parquet')
        
            # Set up the moves dataframe to have temperature and weather conditions (needed later on by
            # the component plotting the trajectories).
            self.moves = move_weather_enrichment(self.moves, weather)
        else :
            self.moves = move_weather_enrichment(self.moves, None)
        
        
        
        ##############################################
        ### ---- SOCIAL MEDIA POST ENRICHMENT ---- ###
        ##############################################
        
        tweets_RDF = None
        print(f"Valore self.tweet_user: {self.tweet_user}")        
        if self.tweet_user :
            print("Enriching users with social media posts!")
            
            tweets = pd.read_parquet(self.upload_users)
            tweets_RDF = tweets.copy()
            
            self.moves['date'] = self.moves['datetime'].dt.date
            tweets['tweet_created'] = tweets['tweet_created'].astype('datetime64')
            tweets['tweet_created'] = tweets['tweet_created'].dt.date
            self.moves['tweet'] = ''

            self.moves.reset_index(inplace=True)  

            self.moves.set_index(['date','uid'],inplace=True)   
            tweets.set_index(['tweet_created','uid'],inplace=True)      
            matched_tweets = self.moves.join(tweets,how='inner')

            self.moves.reset_index(inplace=True)
            matched_tweets.reset_index(inplace=True)

            self.tweets = matched_tweets.copy()    
        
        else :
            self.tweets = None
            
            

        ##############################################
        ###            RDF GRAPH SAVE              ###
        ##############################################
        
        if self.rdf == 'yes':
            
            print("Creating and then saving to disk the RDF graph...")

            # Instantiate RDF-builder
            builder = RDFBuilder()

            # Add the users and the information associated to their raw-trajectories to the graph.
            traj_cleaned = pd.read_parquet('data/temp_dataset/traj_cleaned.parquet')
            builder.add_trajectories(traj_cleaned)

            # Add to the RDF graph the stops, the moves, and the semantic information 
            # associated with the trajectories (social media posts, weather), the stops (type of stop, POIs),
            # and the moves (transportation mean).
            builder.add_occasional_stops(self.mats)
            builder.add_systematic_stops(self.systematic)
            builder.add_moves(self.moves)
            
            # Add weather information to the trajectories.
            if df_weather_enrichment is not None :
                builder.add_weather(df_weather_enrichment)
                
            # Add weather information to the trajectories.
            if tweets_RDF is not None :
                builder.add_social(tweets_RDF)
            
            # Output the RDF graph to disk in Turtle format.
            builder.serialize_graph('kg.ttl')
            
            
        
    def get_users(self):
        self.moves.reset_index(inplace=True)
        return self.moves['uid'].unique()



    def get_trajectories(self,uid):
        return self.moves[self.moves['uid']==uid]['tid'].unique()



    def get_systematic(self,uid):
        return len(self.systematic[self.systematic['uid']==uid])



    def get_occasional(self,uid):
        return len(self.occasional[self.occasional['uid']==uid])



    def get_transport_duration(self,uid):

        first_transport = self.moves[self.moves['uid']==uid].groupby(['label','tid']).first()['datetime']
        last_transport = self.moves[self.moves['uid']==uid].groupby(['label','tid']).last()['datetime']

        duration_tid = last_transport - first_transport
        
        duration = pd.DataFrame(duration_tid.groupby('label').sum())
        duration.reset_index(inplace=True)

        return duration



    def get_tweets(self,uid):
   
        if self.tweets is not None :
            return self.tweets[self.tweets['uid']==uid]['text'].unique()
        else : return []



    def get_mats(self,uid,traj_id):
        #print(self.mats[self.mats['tid']==traj_id])

        return self.moves[(self.moves['uid']==uid)&(self.moves['tid']==traj_id)], self.mats[(self.mats['uid']==uid)&(self.mats['tid']==traj_id)], self.systematic[(self.systematic['uid']==uid)&(self.systematic['tid']==traj_id)]