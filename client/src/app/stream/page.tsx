'use client';

import React, { useCallback, useMemo, useState } from 'react';
import {
  ClientSideRowModelModule,
  ColDef,
  ICellRendererParams,
  ModuleRegistry,
  themeQuartz,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { Title } from '@mantine/core';
import CellButton from '@/components/AgGridCell/CellButton';
import CellLink from '@/components/AgGridCell/CellLink';
import { getUserStreamStatuses, startStream } from '@/api';
import { StreamStatus } from '@/types';
import { StreamStatusEnum } from '@/enum';
import { notifications } from '@mantine/notifications';
import classes from './page.module.css';

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const page = () => {
  const containerStyle = useMemo(() => ({ width: '100%', height: 500 }), []);
  const gridStyle = useMemo(() => ({ height: '100%', width: '100%' }), []);
  const [rowData, setRowData] = useState<StreamStatus[]>([]);
  const defaultColDef = useMemo<ColDef>(() => {
    return {
      flex: 10,
    };
  }, []);
  const [columnDefs] = useState<ColDef[]>([
    {
      field: 'stream_id',
      headerName: 'Stream ID',
      cellRenderer: CellLink,
      cellRendererParams: (params: ICellRendererParams) => ({
        href: `/stream/${params.data.stream_id}`,
        label: params.data.stream_id,
      }),
    },
    {
      field: 'status',
      headerName: 'Stream Status',
    },
    {
      field: 'actions',
      headerName: 'Actions',
      cellRenderer: CellButton,
      cellRendererParams: (params: ICellRendererParams) => ({
        color: 'teal',
        label: 'Start Stream',
        disabled: params.data.status !== StreamStatusEnum.NOT_STARTED,
        handleClick: () => handleCellButtonClick(params.data.stream_id),
      }),
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
    getUserStreamStatuses().then((streamStatuses) => setRowData(streamStatuses));
  }, []);

  const handleCellButtonClick = async (streamId: string) => {
    try {
      const startStreamResponse = await startStream(streamId);
      if (startStreamResponse.status) {
        onGridReady();
        notifications.show({
          color: 'green',
          title: 'Stream started',
          message: `Stream ${streamId} has been started`,
          classNames: classes,
        })
      } else {
        throw new Error(`Failed to start stream ${streamId}`);
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
        notifications.show({
          color: 'red',
          title: 'Failed to start stream',
          message: errorMessage,
          classNames: classes,
        });
    }
  }

  return (
    <>
      <Title order={3} mb={20}>
        Stream Dashboard
      </Title>
      <div style={containerStyle}>
        <div style={gridStyle}>
          <AgGridReact
            theme={myTheme}
            rowData={rowData}
            defaultColDef={defaultColDef}
            columnDefs={columnDefs}
            onGridReady={onGridReady}
          />
        </div>
      </div>
    </>
  );
};

export default page;
