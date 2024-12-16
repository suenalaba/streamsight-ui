import { createFormContext } from '@mantine/form';

interface CreateStreamFormValues {
  dataset_id: string;
  top_k: number;
  metrics: string[];
  background_t: number;
  window_size: number;
  n_seq_data: number;
}

export const [CreateStreamFormProvider, useCreateStreamFormContext, useCreateStreamForm] =
  createFormContext<CreateStreamFormValues>();
