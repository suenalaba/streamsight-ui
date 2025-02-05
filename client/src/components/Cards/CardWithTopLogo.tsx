import React from 'react';
import { Card, CardSection, Flex, Image, Text, Title } from '@mantine/core';

interface CardWithTopLogoProps {
  title: string;
  description: string;
  imgSrc: string;
  imgAlt: string;
  href: string;
}

const CardWithTopLogo = ({ title, description, imgSrc, imgAlt, href }: CardWithTopLogoProps) => {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder component="a" href={href} target="_blank">
      <CardSection>
        <Image src={imgSrc} height={160} alt={imgAlt} />
      </CardSection>
      <Flex align="flex-start" wrap="wrap" gap="md">
        <Flex direction="column" style={{ flex: 1, minWidth: 0 }}>
          <Title order={5} mb={10}>
            {title}
          </Title>
          <Text size="xs">{description}</Text>
        </Flex>
      </Flex>
    </Card>
  );
};

export default CardWithTopLogo;
