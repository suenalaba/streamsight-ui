import React from 'react';
import Link from 'next/link';
import { Badge, Button, Card, Group, Text } from '@mantine/core';

interface GettingStartedCardProps {
  title: string;
  badgeDescription: string;
  badgeColor: string;
  description: string;
  buttonText: string;
  href: string;
}

const GettingStartedCard = ({
  title,
  badgeDescription,
  badgeColor,
  description,
  buttonText,
  href,
}: GettingStartedCardProps) => {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Group justify="space-between" mt="md" mb="xs">
        <Text fw={700}>{title}</Text>
        <Badge color={badgeColor}>{badgeDescription}</Badge>
      </Group>

      <Text size="sm">{description}</Text>

      <Button color="blue" fullWidth mt="md" radius="md" component={Link} href={href}>
        {buttonText}
      </Button>
    </Card>
  );
};

export default GettingStartedCard;
