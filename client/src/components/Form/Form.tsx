import React from 'react';
import {
  Button,
  Group,
  MultiSelect,
  NumberInput,
  Select,
} from '@mantine/core';
import { useForm } from '@mantine/form';

const DATASETS = [
  'amazon_music',
  'amazon_book',
  'amazon_computer',
  'amazon_movie',
  'yelp',
  'test',
  'movielens',
  'lastfm',
];
const METRICS = ['PrecisionK', 'RecallK', 'NDCGK', 'DGCK'];

const Form = () => {
  const form = useForm({
    mode: 'uncontrolled',
    initialValues: {
      datasetId: '',
      topK: 1,
      metrics: [],
      backgroundT: 1,
      windowSize: 1,
      nSeqData: 1,
    },

    validate: {
      datasetId: (value) => (value ? null : 'Dataset ID is required'),
      topK: (value) => (value > 0 ? null : 'Top K must be greater than 0'),
      metrics: (value) => (value.length > 0 ? null : 'At least one metric is required'),
      backgroundT: (value) => (value > 0 ? null : 'Background T must be greater than 0'),
      windowSize: (value) => (value > 0 ? null : 'Window size must be greater than 0'),
      nSeqData: (value) => (value > 0 ? null : 'Number of sequences must be greater than 0'),
    },
  });

  return (
    // eslint-disable-next-line no-console
    <form onSubmit={form.onSubmit((values) => console.log(values))}>
      <Select
        withAsterisk
        label="Dataset"
        placeholder="Select a dataset"
        data={DATASETS}
        clearable
        searchable
        nothingFoundMessage="No dataset found..."
        maxDropdownHeight={200}
        key={form.key('datasetId')}
        {...form.getInputProps('datasetId')}
      />

      <NumberInput label="Top K" placeholder="Input placeholder" key={form.key('topK')}
        {...form.getInputProps('topK')}/>

      <MultiSelect
        withAsterisk
        label="Metrics"
        placeholder="Select metrics"
        data={METRICS}
        clearable
        searchable
        nothingFoundMessage="No metrics found..."
        maxDropdownHeight={200}
        key={form.key('metrics')}
        {...form.getInputProps('metrics')}
      />

      <NumberInput label="Background Timestamp" placeholder="Enter background timestamp" key={form.key('backgroundT')}
        {...form.getInputProps('backgroundT')}/>

      <NumberInput label="Window Size" placeholder="Enter window size" key={form.key('windowSize')}
        {...form.getInputProps('windowSize')}/>

      <NumberInput
        label="Number of sequential data"
        placeholder="Enter number of sequential data"
        key={form.key('nSeqData')}
        {...form.getInputProps('nSeqData')}
      />

      <Group justify="flex-end" mt="md">
        <Button type="submit">Create Stream</Button>
      </Group>
    </form>
  );
};

export default Form;
