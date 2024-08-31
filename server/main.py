from enum import Enum
import io
import json
from typing import List, Optional, cast

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from streamsight.datasets import (AmazonBookDataset, 
                                  AmazonComputerDataset, 
                                  AmazonMovieDataset, 
                                  AmazonMusicDataset, 
                                  YelpDataset)

from streamsight.settings import SlidingWindowSetting
from streamsight.registries.registry import MetricEntry
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from streamsight.algorithms import ItemKNNStatic

from uuid import UUID, uuid4
import pandas as pd

app = FastAPI()

class Metric(str, Enum):
    PrecisionK = "PrecisionK"
    RecallK = "RecallK"
    DCGK = "DCGK"

class Stream(BaseModel):
    dataset_id: str
    top_k: int
    metrics: List[Metric]

dataset_map = {
    'amazon_music': AmazonMusicDataset,
    'amazon_book': AmazonBookDataset,
    'amazon_computer': AmazonComputerDataset,
    'amazon_movie': AmazonMovieDataset,
    'yelp': YelpDataset
}

# stores k:v pair of UUID: EvaluatorStreamer
evaluator_stream_object_map = {}

@app.get("/", tags=["Healthcheck"])
def healthcheck():
    return {"Server is running, STATUS": "HEALTHY"}


@app.post("/streams", tags=["Stream Management"])
def create_stream(stream: Stream):
    try:
        dataset = dataset_map[stream.dataset_id]()
    except KeyError:
        raise HTTPException(status_code=404, detail="Invalid Dataset ID")

    try:
        data = dataset.load()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dataset: {str(e)}")

    try:
        setting_sliding = SlidingWindowSetting(
            background_t=1406851200,
            window_size=60 * 60 * 24 * 300,  # day times N
            n_seq_data=3,
            top_K=stream.top_k,
        )
        setting_sliding.split(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting up sliding window: {str(e)}")

    try:
        metrics = []
        for metric in stream.metrics:
            metrics.append(MetricEntry(metric, K=stream.top_k))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating metrics: {str(e)}")

    try:
        evaluator_streamer = EvaluatorStreamer(metrics, setting_sliding)
        stream_id = uuid4()
        evaluator_stream_object_map[stream_id] = evaluator_streamer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating evaluator streamer: {str(e)}")

    return {"evaluator_stream_id": stream_id}


@app.get("/streams/{stream_id}", tags=["Stream Management"])
def get_stream(stream_id: str):
    try:
        uuid_obj = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer = evaluator_stream_object_map.get(uuid_obj)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    return evaluator_streamer


@app.post("/streams/{stream_id}/start", tags=["Stream Management"])
def start_stream(stream_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        evaluator_streamer.start_stream()
        return {"status": True}
    except Exception as e:
        return {"status": False, "error": f"Error Starting Stream: {str(e)}"}
    

class AlgorithmRegistrationRequest(BaseModel):
    algorithm_name: str

@app.post("/streams/{stream_id}/algorithms", tags=["Algorithm Management"])
def register_algorithm(stream_id: str, request: AlgorithmRegistrationRequest):

    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    algorithm_uuid = evaluator_streamer.register_algorithm(algorithm_name=request.algorithm_name)

    return {"algorithm_uuid": str(algorithm_uuid)}


@app.get("/streams/{stream_id}/algorithms/{algorithm_id}/state", tags=["Algorithm Management"])
def get_algorithm_state(stream_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        algorithm_uuid = UUID(algorithm_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    algorithm_state = evaluator_streamer.get_algorithm_state(algorithm_uuid).name
    return {"algorithm_state": algorithm_state}


@app.get("/streams/{stream_id}/algorithms/state", tags=["Algorithm Management"])
def get_all_algorithm_state(stream_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    algorithm_states = {key: value.name for key, value in evaluator_streamer.get_all_algorithm_status().items()}
    return {"algorithm_states": algorithm_states}


@app.get("/streams/{stream_id}/algorithms/{algorithm_id}/training-data", tags=["Data Handling"])
def get_training_data(stream_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        algorithm_uuid = UUID(algorithm_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    interaction_matrix = evaluator_streamer.get_data(algorithm_uuid)
    df = interaction_matrix.copy_df()

    algo_name = evaluator_streamer.status_registry.get(algorithm_uuid).name
    file_name = f"{algo_name}.csv"

    # Convert DataFrame to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(csv_buffer, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={file_name}"})


@app.get("/streams/{stream_id}/algorithms/{algorithm_id}/unlabeled-data", tags=["Data Handling"])
def get_unlabeled_data(stream_id: str, algorithm_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        algorithm_uuid = UUID(algorithm_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)
    interaction_matrix = evaluator_streamer.get_unlabeled_data(algorithm_uuid)
    df = interaction_matrix.copy_df()

    algo_name = evaluator_streamer.status_registry.get(algorithm_uuid).name
    file_name = f"{algo_name}_unlabeled.csv"

    # Convert DataFrame to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(csv_buffer, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={file_name}"})


@app.post("/streams/{stream_id}/algorithms/{algorithm_id}/predictions", tags=["Predictions"])
async def submit_prediction(stream_id: str, algorithm_id: str, file: UploadFile = File(...)):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        algorithm_uuid = UUID(algorithm_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        # Read the uploaded CSV file into a pandas DataFrame
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        # Ensure the DataFrame has the required columns
        required_columns = {"interactionid", "uid", "iid", "ts"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail="CSV file is missing required columns")

        # TODO: remove this block once https://github.com/HiIAmTzeKean/Streamsight/issues/75 is resolved
        algorithm = ItemKNNStatic()
        algorithm.fit(evaluator_streamer.get_data(algorithm_uuid))
        predictions = algorithm.predict(evaluator_streamer.get_unlabeled_data(algorithm_uuid))
        evaluator_streamer.submit_prediction(algorithm_uuid, predictions)

        assert evaluator_streamer.get_algorithm_state(algorithm_uuid).name == "PREDICTED"
        # evaluator_streamer.submit_prediction(algorithm_uuid, df)
        return {"status": True}
    except Exception as e:
        return {"status": False, "error": f"Error Submitting Prediction: {str(e)}"}


@app.get("/streams/{stream_id}/metrics", tags=["Metrics"])
def get_metrics(stream_id: str):
    try:
        evaluator_streamer_uuid = UUID(stream_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    evaluator_streamer: Optional[EvaluatorStreamer] = evaluator_stream_object_map.get(evaluator_streamer_uuid)
    if not evaluator_streamer:
        raise HTTPException(status_code=404, detail="EvaluatorStreamer not found")

    evaluator_streamer = cast(EvaluatorStreamer, evaluator_streamer)

    try:
        micro_metrics = evaluator_streamer.metric_results("micro")
        macro_metrics = evaluator_streamer.metric_results("macro")

        micro_json = micro_metrics.to_json()
        macro_json = macro_metrics.to_json()

        # Combine both JSON strings into a dictionary
        metrics_dict = {
            "micro_metrics": json.loads(micro_json),
            "macro_metrics": json.loads(macro_json)
        }

        # Convert the dictionary to a JSON string to send to the frontend
        metrics_json = json.dumps(metrics_dict)
        return metrics_json
    except Exception as e:
        return {"status": False, "error": f"Error Getting Metrics: {str(e)}"}
