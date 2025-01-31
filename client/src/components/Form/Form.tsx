import React, { useEffect } from 'react';
import { Button, Flex, Grid, Group, Modal, MultiSelect, NumberInput, Select } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { createStream, getMetricsList } from '@/api';
import { CreateStreamRequest } from '@/types';
import { CreateStreamFormProvider, useCreateStreamForm } from './FormContext';
import classes from './Form.module.css';

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

const Form = () => {
  const [opened, { open, close }] = useDisclosure(false);
  const [createdStreamId, setCreatedStreamId] = React.useState<string | null>(null);
  const [metrics, setMetrics] = React.useState<string[]>([]);

  const form = useCreateStreamForm({
    mode: 'uncontrolled',
    initialValues: {
      dataset_id: '',
      top_k: 1,
      metrics: [],
      background_t: 1,
      window_size: 1,
      n_seq_data: 0,
    },

    validate: {
      dataset_id: (value) => (value ? null : 'Dataset ID is required'),
      top_k: (value) => (value > 0 ? null : 'Top K must be greater than 0'),
      metrics: (value) => (value.length > 0 ? null : 'At least one metric is required'),
      background_t: (value) => (value >= 0 ? null : 'Background T must be greater than 0'),
      window_size: (value) => (value >= 0 ? null : 'Window size must be greater than 0'),
      n_seq_data: (value) => (value >= 0 ? null : 'Number of sequences must be greater than 0'),
    },
  });

  const handleSubmit = async (values: CreateStreamRequest) => {
    try {
      const createStreamResponse = await createStream(values);
      form.reset();
      setCreatedStreamId(createStreamResponse.evaluator_stream_id);
      open();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      notifications.show({
        color: 'red',
        title: 'Failed to create stream',
        message: errorMessage,
        classNames: classes,
      });
    }
  };

  useEffect(() => {
    const fetchMetricsList = async () => {
      try {
        const metricsList = await getMetricsList();
        setMetrics(metricsList);
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        notifications.show({
          color: 'red',
          title: 'Failed to fetch list of available metrics',
          message: errorMessage,
          classNames: classes,
        });
      }
    };
    fetchMetricsList();
  }, []);

  return (
    <>
      <Modal
        opened={opened}
        onClose={close}
        size="lg"
        title="Stream Created"
        overlayProps={{
          backgroundOpacity: 0.55,
          blur: 3,
        }}
      >
        <Flex direction="column" gap="xl">
          Stream Created Successfully: {createdStreamId}
          <Grid>
            <Grid.Col span={4}>
              <Flex direction="column" gap="md">
                <Button variant="outline" onClick={close}>
                  Add Another
                </Button>
                <Button
                  component="a"
                  href={`/stream/${createdStreamId}`}
                  variant="gradient"
                  gradient={{ from: 'blue', to: 'cyan', deg: 90 }}
                >
                  Proceed To Stream
                </Button>
              </Flex>
            </Grid.Col>
          </Grid>
        </Flex>
      </Modal>
      <CreateStreamFormProvider form={form}>
        <form onSubmit={form.onSubmit((values) => handleSubmit(values))}>
          <Select
            withAsterisk
            label="Dataset"
            placeholder="Select a dataset"
            data={DATASETS}
            clearable
            searchable
            nothingFoundMessage="No dataset found..."
            maxDropdownHeight={200}
            key={form.key('dataset_id')}
            {...form.getInputProps('dataset_id')}
          />

          <NumberInput
            label="Top K"
            placeholder="Input placeholder"
            key={form.key('top_k')}
            {...form.getInputProps('top_k')}
          />

          <MultiSelect
            withAsterisk
            label="Metrics"
            placeholder="Select metrics"
            data={metrics}
            clearable
            searchable
            nothingFoundMessage="No metrics found..."
            maxDropdownHeight={200}
            key={form.key('metrics')}
            {...form.getInputProps('metrics')}
          />

          <NumberInput
            label="Background Timestamp"
            placeholder="Enter background timestamp"
            key={form.key('background_t')}
            {...form.getInputProps('background_t')}
          />

          <NumberInput
            label="Window Size"
            placeholder="Enter window size"
            key={form.key('window_size')}
            {...form.getInputProps('window_size')}
          />

          <NumberInput
            label="Number of sequential data"
            placeholder="Enter number of sequential data"
            key={form.key('n_seq_data')}
            {...form.getInputProps('n_seq_data')}
          />

          <Group justify="flex-end" mt="md">
            <Button type="submit" variant="gradient" gradient={{ from: '#1c7ed6', to: '#22b8cf' }}>
              Create Stream
            </Button>
          </Group>
        </form>
      </CreateStreamFormProvider>
    </>
  );
};

export default Form;
