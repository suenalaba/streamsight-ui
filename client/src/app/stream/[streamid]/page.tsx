'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { Container, Flex, Table, Text, Title } from '@mantine/core';

const algorithmStatuses = [
  { algoId: 'algo1', status: 'running' },
  { algoId: 'algo2', status: 'stopped' },
  { algoId: 'algo3', status: 'running' },
  { algoId: 'algo4', status: 'stopped' },
];

const streamSettings = {
  dataset_id: 'string',
  top_k: 3,
  metrics: ['PrecisionK', 'RecallK'],
  background_t: 3,
  window_size: 3,
  n_seq_data: 3,
};

const microResults = [
  { algoId: 'algo1', metric: 'PrecisionK', value: 0.5, num_user: 3 },
  { algoId: 'algo1', metric: 'RecallK', value: 0.5, num_user: 3 },
  { algoId: 'algo2', metric: 'PrecisionK', value: 0.5, num_user: 3 },
  { algoId: 'algo2', metric: 'RecallK', value: 0.5, num_user: 3 },
]

const macroResults = [
  { algoId: 'algo1', metric: 'PrecisionK', value: 0.5, num_window: 3 },
  { algoId: 'algo1', metric: 'RecallK', value: 0.5, num_window: 3 },
  { algoId: 'algo2', metric: 'PrecisionK', value: 0.5, num_window: 3 },
  { algoId: 'algo2', metric: 'RecallK', value: 0.5, num_window: 3 },
]

const page = () => {
  const params = useParams<{ streamid: string }>();
  const streamId = params.streamid;
  const rows = algorithmStatuses.map((element) => (
    <Table.Tr key={`${element.algoId} _status`}>
      <Table.Td>{element.algoId}</Table.Td>
      <Table.Td>{element.status}</Table.Td>
    </Table.Tr>
  ));

  const microRows = microResults.map((element) => (
    <Table.Tr key={`${element.algoId} _micro_metrics_${element.metric}`}>
      <Table.Td>{element.algoId}</Table.Td>
      <Table.Td>{element.metric}</Table.Td>
      <Table.Td>{element.value}</Table.Td>
      <Table.Td>{element.num_user}</Table.Td>
    </Table.Tr>
  ));

  const macroRows = macroResults.map((element) => (
    <Table.Tr key={`${element.algoId} _macro_metrics_${element.metric}`}>
      <Table.Td>{element.algoId}</Table.Td>
      <Table.Td>{element.metric}</Table.Td>
      <Table.Td>{element.value}</Table.Td>
      <Table.Td>{element.num_window}</Table.Td>
    </Table.Tr>
  ));

  return (
    <>
        <Title order={3}>
          Stream ID:{' '}
          <Text span variant="gradient" gradient={{ from: '#1c7ed6', to: '#22b8cf' }} inherit>
            {streamId}
          </Text>{' '}
        </Title>

        <Container size="lg" style={{ marginLeft: 0, paddingLeft: 0, marginTop: 20 }}>
          <Title order={3}>Algorithm Statuses</Title>
          <Table highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Algorithm ID</Table.Th>
                <Table.Th>Status</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{rows}</Table.Tbody>
          </Table>
        </Container>

        <Container size="lg" style={{ marginLeft: 0, paddingLeft: 0, marginTop: 20 }}>
          <Flex justify="flex-start" direction="column">
            <Title order={3}>Stream Settings</Title>
            <Table variant="vertical" layout="fixed" withTableBorder withColumnBorders striped>
              <Table.Tbody>
                {Object.entries(streamSettings).map(([key, value]) => (
                  <Table.Tr key={key}>
                    <Table.Th w={160}>{key}</Table.Th>
                    <Table.Td>
                      {Array.isArray(value) ? value.join(', ') : value.toString()}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Flex>
        </Container>

        <Container size="lg" style={{ marginLeft: 0, paddingLeft: 0, marginTop: 20 }}>
          <Title order={3}>Macro Metrics</Title>
          <Table highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Algorithm ID</Table.Th>
                <Table.Th>Metric</Table.Th>
                <Table.Th>Value</Table.Th>
                <Table.Th>Number of Windows</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{macroRows}</Table.Tbody>
          </Table>
        </Container>

        <Container size="lg" style={{ marginLeft: 0, paddingLeft: 0, marginTop: 20 }}>
          <Title order={3}>Micro Metrics</Title>
          <Table highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Algorithm ID</Table.Th>
                <Table.Th>Metric</Table.Th>
                <Table.Th>Value</Table.Th>
                <Table.Th>Number of Users</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{microRows}</Table.Tbody>
          </Table>
        </Container>
    </>
  );
};

export default page;
