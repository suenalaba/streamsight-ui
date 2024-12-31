import { AlgorithmState, StreamStatusEnum } from './enum';

export interface CreateStreamRequest {
  dataset_id: string;
  top_k: number;
  metrics: string[];
  background_t: number;
  window_size: number;
  n_seq_data: number;
}

export interface CreateStreamResponse {
  evaluator_stream_id: string;
}

export interface StartStreamResponse {
  status: boolean;
}

export interface StreamSettings {
  dataset_id: string;
  top_k: number;
  metrics: string[];
  background_t: number;
  window_size: number;
  n_seq_data: number;
}

export interface RegisterAlgorithmRequest {
  algorithm_name: string;
}

export interface RegisterAlgorithmResponse {
  algorithm_uuid: string;
}

export interface GetAllAlgorithmStateResponse {
  algorithm_states: AlgorithmUuidToState[];
}

export interface AlgorithmUuidToState {
  algorithm_uuid: string;
  algorithm_name: string;
  state: AlgorithmState;
}

export interface StreamStatus {
  stream_id: string;
  status: StreamStatusEnum;
}

interface Metric {
  algorithm_name: string;
  algorithm_id: string;
  metric: string;
}
export interface MacroMetric extends Metric {
  macro_score: number;
  num_window: number;
}

export interface MicroMetric extends Metric {
  micro_score: number;
  num_user: number;
}

export interface Metrics {
  micro_metrics: MicroMetric[];
  macro_metrics: MacroMetric[];
}
