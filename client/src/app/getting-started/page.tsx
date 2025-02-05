import React from 'react';
import { SimpleGrid, Title } from '@mantine/core';
import GettingStartedCard from '@/components/GettingStartedCard/GettingStartedCard';

const cards = [
  {
    title: 'Full User Flow',
    badgeDescription: 'Popular',
    badgeColor: 'pink',
    description:
      'Find out how to use Streamsight to its full potential including the full user flow on how to use Streamsight',
    buttonText: 'Explore more now',
    href: '/full-flow-guide',
  },
  {
    title: 'Settings Configuration',
    badgeDescription: 'Guide',
    badgeColor: 'green',
    description:
      'Discover the available settings in Streamsight and learn how to configure stream settings in Streamsight to align with your research goals.',
    buttonText: 'Explore settings configurations',
    href: '/settings-configuration-guide',
  },
  {
    title: 'Notebooks',
    badgeDescription: 'Popular',
    badgeColor: 'pink',
    description: 'Find out how to use Streamsight to its full potential',
    buttonText: 'Explore more now',
    href: '/notebooks',
  },
  {
    title: 'Create Your Own Algorithm',
    badgeDescription: 'Popular',
    badgeColor: 'pink',
    description: 'Find out how to use Streamsight to its full potential',
    buttonText: 'Explore more now',
    href: '/public-api',
  },
];

const page = () => {
  return (
    <>
      <Title order={1} mb={20}>
        How To Use Streamsight
      </Title>
      <SimpleGrid cols={2} spacing="lg" verticalSpacing="lg">
        {cards.map((card) => (
          <GettingStartedCard
            key={card.title}
            title={card.title}
            badgeDescription={card.badgeDescription}
            badgeColor={card.badgeColor}
            description={card.description}
            buttonText={card.buttonText}
            href={card.href}
          />
        ))}
      </SimpleGrid>
    </>
  );
};

export default page;
