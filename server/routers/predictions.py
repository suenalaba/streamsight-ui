import io
from typing import Optional, cast
from uuid import UUID
from fastapi import APIRouter, File, HTTPException, UploadFile
import pandas as pd
from streamsight.evaluators.evaluator_stream import EvaluatorStreamer
from streamsight.algorithms import ItemKNNStatic
from constants import evaluator_stream_object_map

router = APIRouter(
  tags=["Predictions"]
)

@router.post("/streams/{stream_id}/algorithms/{algorithm_id}/predictions")
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

