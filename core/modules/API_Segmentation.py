import pandas as pd

from pydantic import BaseModel, Field
from fastapi import FastAPI, APIRouter, UploadFile, File, Query, Depends

from .Segmentation import Segmentation


class API_Segmentation(Segmentation) :
    '''
    This class exposes the functionalities provided by the Segmentation module via an API endpoint.
    '''

    ### INNER CLASSES ###

    class Params(BaseModel):
        min_duration_stop: int = Field(Query(..., description="Minimum duration of a stop (in minutes)."))
        max_stop_radius: float = Field(Query(..., description="Maximum radius a stop can have (in kilometers)"))

    class Results(BaseModel):
        stops : dict = Field(description="pandas DataFrame (translated in JSON) containing the stop segments.")
        moves : dict = Field(description="pandas DataFrame (translated in JSON) containing the move segments.")



    ### PUBLIC CLASS CONSTRUCTOR ###

    def __init__(self, router : APIRouter):

        # Execute the superclass constructor.
        super().__init__()


        # Set up the HTTP responses that can be sent to the requesters.
        responses = {500: {"description" : "Some error occurred during the trajectory segmentation. Check the correctness of the trajectory dataset being passed!"}}

        # Declare the path function operations associated with the API_Preprocessing class.
        @router.get("/" + Segmentation.id_class + "/",
                    description="This path operation segments a dataset of trajectories into stop and move segments. The operation returns the pandas DataFrames of the stops and the moves translated into the JSON format.",
                    responses=responses)
        def segment(file_trajectories : UploadFile = File(description="pandas DataFrame, stored in a Parquet file, containing a dataset of trajectories."),
                    params: API_Segmentation.Params = Depends()) -> API_Segmentation.Results:

            # Here we execute the internal code of the Preprocessing subclass to do the trajectory preprocessing...
            params_segmentation = {'trajectories': pd.read_parquet(file_trajectories.file),
                                   'duration': params.min_duration_stop,
                                   'radius': params.max_stop_radius}

            self.execute(params_segmentation)


            # Construct the (dict) response, containing the stops and moves dataframes (will be automatically translated to JSON by FastAPI).
            results = {'stops' : self.stops.to_dict(),
                       'moves' : self.moves.to_dict()}

            # Reset the object internal state.
            self.reset_state()

            # Return the results.
            return results