'use client';

import { useEffect, useState } from 'react';
import { Button, Text } from '@mantine/core';
import { getHeroes, getStatus } from '@/api';
import { Welcome } from '@/components/Welcome/Welcome';

export default function Home() {
  const [status, setStatus] = useState('loading');

  const fetchStatus = async () => {
    try {
      await getStatus();
      setStatus('success');
    } catch (error) {
      setStatus('error');
    }
  };

  const fetchHeroes = async () => {
    try {
      const heroes = await getHeroes();
      console.log('Heroes', heroes);
    } catch (error) {
      console.error('Error fetching heroes', error);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <>
      <Welcome />
      <Text>{`Healthcheck status: ${status}`}</Text>
      <Button onClick={fetchHeroes}>Fetch heroes from supabase</Button>
    </>
  );
}
