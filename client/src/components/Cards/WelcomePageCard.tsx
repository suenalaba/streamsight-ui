import React from 'react';
import { Avatar, Card, Flex, Image, Text } from '@mantine/core';

interface WelcomePageCardProps {
  title: string;
  description: string;
  imgSrc: string;
  imgAlt: string;
  href: string;
  displayAsAvatar?: boolean;
  icon?: any;
}

const WelcomePageCard = ({
  title,
  description,
  imgSrc,
  imgAlt,
  href,
  displayAsAvatar = false,
  icon,
}: WelcomePageCardProps) => {
  const imageDisplay = () => {
    if (displayAsAvatar) {
      if (icon) {
        return (
          <Avatar color="blue" radius="sm">
            {icon}
          </Avatar>
        );
      }
      return <Avatar src={imgSrc} radius="xl" alt={imgAlt} />;
    }
    return <Image src={imgSrc} alt={imgAlt} h={48} w={48} />;
  };
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder component="a" href={href} target="_blank">
      <Flex align="flex-start" wrap="wrap" gap="md">
        <Flex direction="column" style={{ flex: 1, minWidth: 0 }}>
          <Text size="xl" fw={700} mb={10}>
            {title}
          </Text>
          <Text size="xs">{description}</Text>
        </Flex>
        {imageDisplay()}
      </Flex>
    </Card>
  );
};

export default WelcomePageCard;
