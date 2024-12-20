'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import {
  ClientSideRowModelModule,
  ColDef,
  ModuleRegistry,
  NumberFilterModule,
  TextFilterModule,
  themeQuartz,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { Badge, Container, Flex, Group, Table, Text, Title } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { getAlgorithmStates, getMetrics, getStreamSettings, getStreamStatus } from '@/api';
import RegisterAlgoForm from '@/components/RegisterAlgoForm/RegisterAlgoForm';
import {
  RegisterAlgoFormProvider,
  useRegisterAlgoForm,
} from '@/components/RegisterAlgoForm/RegisterAlgoFormContext';
import {
  AlgorithmUuidToState,
  MacroMetric,
  MicroMetric,
  StreamSettings,
} from '@/types';
import classes from './page.module.css';

import 'ag-grid-community/styles/ag-theme-alpine.css';

import { StreamStatusEnum } from '@/enum';
import { getStatusBadgeProps } from '@/constants';

ModuleRegistry.registerModules([
  ClientSideRowModelModule,
  ClientSideRowModelModule,
  NumberFilterModule,
  TextFilterModule,
]);

const page = () => {
  const params = useParams<{ streamid: string }>();
  const streamId = params.streamid;

  const [streamSettings, setStreamSettings] = useState<StreamSettings | null>(null);
  const [algorithmStates, setAlgorithmStates] = useState<AlgorithmUuidToState[]>([]);
  const [streamStatus, setStreamStatus] = useState<string>('');

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
    };

    const fetchStreamStatus = async () => {
      try {
        setStreamStatus((await getStreamStatus(streamId)).status);
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        notifications.show({
          color: 'red',
          title: 'Failed to get stream status',
          message: errorMessage,
          classNames: classes,
        });
      }
    };

    if (streamId) {
      fetchStreamSettings();
      fetchAlgorithmStates();
      fetchStreamStatus();
    }
  }, [streamId]);

  const statusBadgeProps = getStatusBadgeProps(streamStatus as StreamStatusEnum);

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

  // Macro and Micro Metrics Table
  const containerStyle = useMemo(() => ({ width: '100%', height: 300 }), []);
  const gridStyle = useMemo(() => ({ height: '100%', width: '100%' }), []);
  const [macroTableRowData, setMacroTableRowData] = useState<MacroMetric[]>([]);
  const [microTableRowData, setMicroTableRowData] = useState<MicroMetric[]>([]);

  const defaultColDef = useMemo<ColDef>(() => {
    return {
      flex: 10,
      filter: 'agTextColumnFilter',
    };
  }, []);
  const [macroTableColumnDefs] = useState<ColDef[]>([
    {
      field: 'algorithm_name',
      headerName: 'Algorithm Name',
    },
    {
      field: 'algorithm_id',
      headerName: 'Algorithm ID',
    },
    {
      field: 'metric',
      headerName: 'Metric',
    },
    {
      field: 'macro_score',
      headerName: 'Macro Score',
      filter: 'agNumberColumnFilter',
    },
    {
      field: 'num_window',
      headerName: 'Number of Windows',
      filter: 'agNumberColumnFilter',
    },
  ] as ColDef[]);

  const [microTableColumnDefs] = useState<ColDef[]>([
    {
      field: 'algorithm_name',
      headerName: 'Algorithm Name',
    },
    {
      field: 'algorithm_id',
      headerName: 'Algorithm ID',
    },
    {
      field: 'metric',
      headerName: 'Metric',
    },
    {
      field: 'micro_score',
      headerName: 'Micro Score',
      filter: 'agNumberColumnFilter',
    },
    {
      field: 'num_user',
      headerName: 'Number of Users',
      filter: 'agNumberColumnFilter',
    },
  ] as ColDef[]);

  const myTheme = themeQuartz.withParams({
    backgroundColor: 'white',
    foregroundColor: 'black',
    headerTextColor: 'black',
    headerBackgroundColor: '#00FFCA',
    oddRowBackgroundColor: 'rgb(0, 0, 0, 0.03)',
    headerColumnResizeHandleColor: '#05BFDB',
  });

  const onGridReady = useCallback(() => {
    getMetrics(streamId).then((metrics) => {
      if (!metrics) {
        return;
      }
      setMacroTableRowData(metrics.macro_metrics);
      setMicroTableRowData(metrics.micro_metrics);
    }).catch((error: unknown) => {
      const errorMessage = error instanceof Error ? error.message : String(error);
      notifications.show({
        color: 'red',
        title: 'Failed to get metrics',
        message: errorMessage,
        classNames: classes,
      });
    });
  }, []);

  return (
    <>
      <Container size="lg" style={{ marginLeft: 0, paddingLeft: 0 }}>
      <Group justify="space-between">
          <Title order={3}>
            Stream ID:{' '}
            <Text span variant="gradient" gradient={{ from: '#1c7ed6', to: '#22b8cf' }} inherit>
              {streamId}
            </Text>{' '}
          </Title>
          <Badge color={statusBadgeProps?.color} size="xl">{statusBadgeProps?.label}</Badge>
      </Group>
      </Container>

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
          <RegisterAlgoForm streamStatus={streamStatus}/>
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
        <div style={containerStyle}>
          <div style={gridStyle}>
            <AgGridReact
              theme={myTheme}
              rowData={macroTableRowData}
              defaultColDef={defaultColDef}
              columnDefs={macroTableColumnDefs}
              onGridReady={onGridReady}
            />
          </div>
        </div>
      </Container>

      <Container size="lg" style={{ marginLeft: 0, paddingLeft: 0, marginTop: 20 }}>
        <Title order={3}>Micro Metrics</Title>
        <div style={containerStyle}>
          <div style={gridStyle}>
            <AgGridReact
              theme={myTheme}
              rowData={microTableRowData}
              defaultColDef={defaultColDef}
              columnDefs={microTableColumnDefs}
              onGridReady={onGridReady}
              className="ag-theme-alpine"
            />
          </div>
        </div>
      </Container>
    </>
  );
};

export default page;
