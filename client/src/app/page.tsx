'use client';

import { getStatus } from '@/api';
import { Welcome } from '@/components/Welcome/Welcome';
import { Text } from '@mantine/core';
import { useEffect, useState } from 'react';

export default function Home() {
  const [status, setStatus] = useState('loading');

  const fetchStatus = async () => {
    try {
      await getStatus();
      setStatus('success');
    } catch (error) {
      setStatus('error');
    }
  }

  useEffect(() => {
    fetchStatus();
  },[]);

  return (
    <>
      <Welcome />
      <Text>{`Healthcheck status: ${status}`}</Text>
    </>
  );
}
