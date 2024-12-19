'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Container, Flex, Table, Text, Title } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { getAlgorithmStates, getStreamSettings } from '@/api';
import { AlgorithmUuidToState, StreamSettings } from '@/types';
import classes from './page.module.css';
import { RegisterAlgoFormProvider, useRegisterAlgoForm } from '@/components/RegisterAlgoForm/RegisterAlgoFormContext';
import RegisterAlgoForm from '@/components/RegisterAlgoForm/RegisterAlgoForm';

const microResults = [
  { algoId: 'algo1', metric: 'PrecisionK', value: 0.5, num_user: 3 },
  { algoId: 'algo1', metric: 'RecallK', value: 0.5, num_user: 3 },
  { algoId: 'algo2', metric: 'PrecisionK', value: 0.5, num_user: 3 },
  { algoId: 'algo2', metric: 'RecallK', value: 0.5, num_user: 3 },
];

const macroResults = [
  { algoId: 'algo1', metric: 'PrecisionK', value: 0.5, num_window: 3 },
  { algoId: 'algo1', metric: 'RecallK', value: 0.5, num_window: 3 },
  { algoId: 'algo2', metric: 'PrecisionK', value: 0.5, num_window: 3 },
  { algoId: 'algo2', metric: 'RecallK', value: 0.5, num_window: 3 },
];

const page = () => {
  const params = useParams<{ streamid: string }>();
  const streamId = params.streamid;

  const [streamSettings, setStreamSettings] = useState<StreamSettings | null>(null);
  const [algorithmStates, setAlgorithmStates] = useState<AlgorithmUuidToState[]>([]);

  useEffect(() => {
    const fetchStreamSettings = async () => {
      try {
        setStreamSettings(await getStreamSettings(streamId));
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        notifications.show({
          color: 'red',
          title: 'Failed to get stream settings',
          message: errorMessage,
          classNames: classes,
        });
      }
    };

    const fetchAlgorithmStates = async () => {
      try {
        setAlgorithmStates(await getAlgorithmStates(streamId));
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        notifications.show({
          color: 'red',
          title: 'Failed to get algorithm states',
          message: errorMessage,
          classNames: classes,
        });
      }
    }

    if (streamId) {
      fetchStreamSettings();
      fetchAlgorithmStates();
    }
  }, [streamId]);

  const form = useRegisterAlgoForm({
    mode: 'uncontrolled',
    initialValues: {
      algorithm_name: '',
    },

    validate: {
      algorithm_name: (value) => (value ? null : 'Algorithm Name is required'),
    },
  });

  const rows = algorithmStates.map((algorithmState) => (
    <Table.Tr key={`${algorithmState.algorithm_uuid} _status`}>
      <Table.Td>{algorithmState.algorithm_uuid}</Table.Td>
      <Table.Td>{algorithmState.algorithm_name}</Table.Td>
      <Table.Td>{algorithmState.state}</Table.Td>
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
              <Table.Th>Algorithm Name</Table.Th>
              <Table.Th>Status</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{rows}</Table.Tbody>
        </Table>
        <RegisterAlgoFormProvider form={form}>
          <RegisterAlgoForm/>
        </RegisterAlgoFormProvider>
      </Container>

      <Container size="lg" style={{ marginLeft: 0, paddingLeft: 0, marginTop: 20 }}>
        <Flex justify="flex-start" direction="column">
          <Title order={3}>Stream Settings</Title>
          <Table variant="vertical" layout="fixed" withTableBorder withColumnBorders striped>
            <Table.Tbody>
              {streamSettings &&
                Object.entries(streamSettings).map(([key, value]) => (
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
