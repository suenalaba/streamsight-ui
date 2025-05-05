'use client';

import { useEffect, useState } from 'react';
import { Button, Text } from '@mantine/core';
import { getHeroes, getStatus } from '@/api';

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
      <Text>{`Healthcheck status: ${status}`}</Text>
      <Button color="rgba(0, 61, 245, 1)" onClick={fetchHeroes}>
        Fetch heroes from supabase
      </Button>
    </>
  );
}