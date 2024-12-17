import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { Button, Flex, Group, Modal, Text, TextInput } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { registerAlgorithm } from '@/api';
import { RegisterAlgoFormValues, useRegisterAlgoFormContext } from './RegisterAlgoFormContext';
import classes from './RegisterAlgoForm.module.css';

const RegisterAlgoForm = () => {
  const form = useRegisterAlgoFormContext();
  const streamId = useParams<{ streamid: string }>().streamid;

  const [opened, { open, close }] = useDisclosure(false);
  const [registeredAlgorithmId, setRegisteredAlgorithmId] = useState<string | null>(null);
  const [registeredAlgorithmName, setRegisteredAlgorithmName] = useState<string | null>(null);

  form.watch('algorithm_name', ({ value }) => {
    setRegisteredAlgorithmName(value);
  });

  const handleSubmit = async (values: RegisterAlgoFormValues) => {
    try {
      const registerAlgorithmResponse = await registerAlgorithm(streamId, values);
      form.reset();
      setRegisteredAlgorithmId(registerAlgorithmResponse.algorithm_uuid);
      open();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      notifications.show({
        color: 'red',
        title: `Failed to register algorithm to stream: ${streamId}`,
        message: errorMessage,
        classNames: classes,
      });
    }
  };

  return (
    <>
      <Modal
        opened={opened}
        onClose={close}
        size="lg"
        title="Algorithm Registered"
        overlayProps={{
          backgroundOpacity: 0.55,
          blur: 3,
        }}
      >
        <Flex direction="column" gap="sm">
          <Text>Algorithm Registered Successfully!</Text>
          <Flex gap="sm">
            <Text>Algorithm Name: </Text>
            <Text variant="gradient" gradient={{ from: 'blue', to: 'cyan', deg: 90 }}>
              {registeredAlgorithmName}
            </Text>
          </Flex>
          <Flex gap="sm">
          <Text>
            Algorithm ID:{' '}
          </Text>
            <Text variant="gradient" gradient={{ from: 'blue', to: 'cyan', deg: 90 }}>
              {registeredAlgorithmId}
            </Text>
          </Flex>
        </Flex>
      </Modal>
      <form onSubmit={form.onSubmit((values) => handleSubmit(values))}>
        <TextInput
          label="Register New Algorithm"
          placeholder="Algorithm Name"
          key={form.key('algorithm_name')}
          {...form.getInputProps('algorithm_name')}
        />

        <Group justify="flex-end" mt="md">
          <Button type="submit" variant="gradient" gradient={{ from: '#1c7ed6', to: '#22b8cf' }}>
            Register Algorithm
          </Button>
        </Group>
      </form>
    </>
  );
};

export default RegisterAlgoForm;
