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

interface IRow {
  streamId: string;
  streamStatus: string;
}

const streamSettingsData = [
  { streamId: 'stream1', streamStatus: 'started' },
  { streamId: 'stream2', streamStatus: 'not_started' },
  { streamId: 'stream3', streamStatus: 'started' },
  { streamId: 'stream4', streamStatus: 'not_started' },
];

ModuleRegistry.registerModules([ClientSideRowModelModule]);

const page = () => {
  const containerStyle = useMemo(() => ({ width: '100%', height: 500 }), []);
  const gridStyle = useMemo(() => ({ height: '100%', width: '100%' }), []);
  const [rowData, setRowData] = useState<any[]>([] as IRow[]);
  const defaultColDef = useMemo<ColDef>(() => {
    return {
      flex: 10,
    };
  }, []);
  const [columnDefs] = useState<ColDef[]>([
    {
      field: 'streamId',
      headerName: 'Stream ID',
      cellRenderer: CellLink,
      cellRendererParams: (params: ICellRendererParams) => ({
        href: `/stream/${params.data.streamId}`,
        label: params.data.streamId,
      }),
    },
    {
      field: 'streamStatus',
      headerName: 'Stream Status',
    },
    {
      field: 'actions',
      headerName: 'Actions',
      cellRenderer: CellButton,
      cellRendererParams: (params: ICellRendererParams) => ({
        color: 'teal',
        label: 'Start Stream',
        disabled: params.data.streamStatus === 'started',
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
    setRowData(streamSettingsData);
  }, []);

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
