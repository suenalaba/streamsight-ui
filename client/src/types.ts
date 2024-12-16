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
