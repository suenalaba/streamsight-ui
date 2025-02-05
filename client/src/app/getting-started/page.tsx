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
    imgSrc: '/getting-started/full-flow.jpg',
    imgAlt: 'Full User Flow',
  },
  {
    title: 'Settings Configuration',
    badgeDescription: 'Guide',
    badgeColor: 'green',
    description:
      'Discover the available settings in Streamsight and learn how to configure stream settings in Streamsight to align with your research goals.',
    buttonText: 'Explore settings configurations',
    href: '/settings-configuration-guide',
    imgSrc: '/getting-started/settings.jpg',
    imgAlt: 'Settings Configuration Guide',
  },
  {
    title: 'Notebooks',
    badgeDescription: 'Popular',
    badgeColor: 'pink',
    description: 'Find out how to use Streamsight to its full potential',
    buttonText: 'Explore more now',
    href: '/notebooks',
    imgSrc: '/getting-started/create-own-algorithm.jpg',
    imgAlt: 'Create Your Own Algorithm',
  },
  {
    title: 'Create Your Own Algorithm',
    badgeDescription: 'Guide',
    badgeColor: 'green',
    description:
      'Find out how to create your own RecSys algorithm and integrate it with Streamsight to evaluate your algorithms.',
    buttonText: 'Create your algorithm now',
    href: '/create-algorithm-guide',
    imgSrc: '/getting-started/create-own-algorithm.jpg',
    imgAlt: 'Create Your Own Algorithm',
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
            imgSrc={card.imgSrc}
            imgAlt={card.imgAlt}
          />
        ))}
      </SimpleGrid>
    </>
  );
};

export default page;
