import React from 'react';
import Link from 'next/link';
import { Badge, Button, Card, CardSection, Group, Image, Text } from '@mantine/core';

interface GettingStartedCardProps {
  title: string;
  badgeDescription: string;
  badgeColor: string;
  description: string;
  buttonText: string;
  href: string;
  imgSrc: string;
  imgAlt: string;
}

const GettingStartedCard = ({
  title,
  badgeDescription,
  badgeColor,
  description,
  buttonText,
  href,
  imgSrc,
  imgAlt,
}: GettingStartedCardProps) => {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <CardSection>
        <Image src={imgSrc} height={160} alt={imgAlt} />
      </CardSection>

      <Group justify="space-between" mt="md" mb="xs">
        <Text fw={700}>{title}</Text>
        <Badge color={badgeColor}>{badgeDescription}</Badge>
      </Group>

      <Text size="sm">{description}</Text>

      <Button color="cyan" fullWidth mt="md" radius="md" component={Link} href={href}>
        {buttonText}
      </Button>
    </Card>
  );
};

export default GettingStartedCard;
