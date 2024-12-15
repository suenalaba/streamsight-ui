'use client';

import React from 'react';
import { Container, Text, Title } from '@mantine/core';
import Form from '@/components/Form/Form';
import styles from './styles.module.css';

const page = () => {
  return (
    <>
      <Title className={styles.title} ta="center" mt={100}>
        <Text
          inherit
          variant="gradient"
          component="span"
          gradient={{ from: '#1c7ed6', to: '#22b8cf' }}
        >
          Create Stream
        </Text>
      </Title>
      <Container size="md">
        <Form />
      </Container>
    </>
  );
};

export default page;
