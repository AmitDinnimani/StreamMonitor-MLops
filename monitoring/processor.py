import json
import time
import sqlite3
import threading
from pathlib import Path
from db import get_connection,init_db,add_metric,add_prediction
from sklearn.datasets import fetch_california_housing
from streaming_median import StreamingMedian
import pandas as pd
import numpy as np
from metrics_queue import STREAM_BUFFER,add_in_queue,get_features_df

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR/'monitoring'/'monitoring.db'


data = fetch_california_housing(as_frame=True)

df = data.data

BASELINE_MEDIAN = df.median().tolist()
BASELINE_MEAN =  df.mean().tolist()
BASELINE_STD = df.var(ddof=0).tolist()

class MetricsProcessor:

    def __init__(self,drift_threshold,global_threshold):
        init_db()

        self.queue_data_threshold = 500
        self.stream_buffer = STREAM_BUFFER
        self.drift_threshold = drift_threshold
        self.golbal_threshold = global_threshold
        
    def get_drift_value(self, baseline, streaming):
        return [abs(b - s) for b, s in zip(baseline, streaming)]


    def backend_ops(self, prediction_request,prediction_value,request_id):

        add_in_queue(self.stream_buffer,prediction_request,prediction_value,request_id)

        if len(self.stream_buffer) > self.queue_data_threshold:

            streaming_df = get_features_df(self.stream_buffer)
 
            streaming_mean = []
            streaming_median = []
            streaming_std = []

            for col in streaming_df.columns:

                values = streaming_df[col].values

                sm = StreamingMedian()

                for v in values:
                    sm.insert(v)

                streaming_mean.append(values.mean())
                streaming_median.append(sm.get_median())
                streaming_std.append(values.var(ddof=0))

            mean_drift_val = self.get_drift_value(BASELINE_MEAN,streaming_mean)
            median_drift_val = self.get_drift_value(BASELINE_MEDIAN,streaming_median)
            std_drift_val = self.get_drift_value(BASELINE_STD,streaming_std)

            mean_feature_alerts = [ d > self.drift_threshold for d in mean_drift_val]
            median_feature_alerts = [ d > self.drift_threshold for d in median_drift_val]
            std_feature_alerts = [d > self.drift_threshold for d in std_drift_val]

            mean_ratio   = sum(mean_feature_alerts)   / len(mean_feature_alerts)
            median_ratio = sum(median_feature_alerts) / len(median_feature_alerts)
            std_ratio    = sum(std_feature_alerts)    / len(std_feature_alerts)

            drift_score = max(mean_ratio, median_ratio)
            global_alert = int(drift_score >= 0.3)

            add_metric(
                timestamp = time.time(),
                median_value = np.mean(streaming_median),
                mean_value = np.mean(streaming_mean),
                std_value = np.mean(streaming_std),
                drift_score = drift_score,
                mean_ratio = mean_ratio,
                median_ratio = median_ratio,
                std_ratio = std_ratio,
                alert = global_alert,
                mean_drift_vals = json.dumps(mean_drift_val),
                median_drift_vals = json.dumps(median_drift_val),
                std_drift_vals = json.dumps(std_drift_val)
            )


        add_prediction(prediction_request,prediction_value,request_id)