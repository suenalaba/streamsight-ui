import React from 'react';
import {
  Divider,
  Image,
  Table,
  TableTbody,
  TableTd,
  TableTh,
  TableTr,
  Text,
  Title,
} from '@mantine/core';

const streamSettings = [
  {
    settingName: 'n_seq_data',
    description:
      'Number of last interactions to provide as data for model to make prediction. Usually 0.',
  },
  {
    settingName: 'window_size',
    description:
      'Size of the window in seconds to slide over the data. Affects the incremental data being released to the model. Usually X years, X months, X weeks or X days.',
  },
  {
    settingName: 'background_t',
    description:
      'Timestamp in epoch seconds of initial Data used for training the model. This is the amount of background data you require.',
  },
  {
    settingName: 'top_k',
    description: 'The K value that will be used by default for evaluation metrics.',
  },
  {
    settingName: 'metrics',
    description:
      'The evaluation metrics that the stream will use. For example, precision, recall, ndcg, dcg and hit ratio, etc.',
  },
  {
    settingName: 'dataset_id',
    description:
      'The dataset that the stream will use for evaluation. For example, amazon_music, lastfm2k, movielens100k, etc.',
  },
  {
    settingName: 'number_of_windows',
    description:
      'Depending on the window size, the number of windows/splits that will be used for evaluation. This is also the number of iterations the stream will need to process until completion.',
  },
  {
    settingName: 'current_window',
    description: 'The current window that the stream is at. If 0 means the stream has not started.',
  },
];

const page = () => {
  return (
    <>
      <Title order={1} mb={20}>
        How To Use Streamsight
      </Title>
      <Divider my="md" />
      <Title order={3} mb={20}>
        Settings Configuration Guide
        <Text fw={700}>
          Discover the available settings in Streamsight and learn how to configure stream settings
          in Streamsight to align with your research goals.
        </Text>
      </Title>
      <Image
        src="/getting-started/settings.jpg"
        alt="Settings Configuration Guide"
        h={200}
        radius="md"
      />
      <Divider my="md" />
      <Table variant="vertical" layout="fixed" withTableBorder withColumnBorders striped>
        <TableTbody>
          {streamSettings &&
            streamSettings.map(({ settingName, description }) => (
              <TableTr key={settingName}>
                <TableTh w={160}>{settingName}</TableTh>
                <TableTd>{description}</TableTd>
              </TableTr>
            ))}
        </TableTbody>
      </Table>
    </>
  );
};

export default page;
