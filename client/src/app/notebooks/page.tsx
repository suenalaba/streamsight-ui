import React from 'react';
import Link from 'next/link';
import { IconCode, IconPlus } from '@tabler/icons-react';
import { Button, Divider, Grid, GridCol, Group, Image, Text, Title } from '@mantine/core';
import CardWithTopLogo from '@/components/Cards/CardWithTopLogo';

const notebookCards = [
  {
    title: 'RecentPop Algorithm with MovieLens Dataset',
    description:
      'Demonstration of the RecentPop algorithm baseline using the MovieLens dataset. This offers a different perspective of the Popularity baseline.',
    imgSrc: '/dataset-card/movielens.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/examples/movielens_recentpop.ipynb',
  },
  {
    title: 'DecayPop Algorithm with MovieLens Dataset',
    description:
      'Demonstration of the DecayPop algorithm baseline using the MovieLens dataset. This offers a different perspective of the Popularity baseline.',
    imgSrc: '/dataset-card/movielens.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/examples/movielens_decaypop.ipynb',
  },
  {
    title: 'ItemKNN Incremental (RecentPop Padding) with MovieLens Dataset',
    description:
      'ItemKNN incremental algorithm that pads unknown users with RecentPop Algorithm benchmarked with the MovieLens dataset.',
    imgSrc: '/dataset-card/movielens.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/examples/movielens_itemknn_incremental_randompad.ipynb',
  },
  {
    title: 'ItemKNN Incremental (Metadata Padding) with MovieLens Dataset',
    description:
      'A demonstration of the ItemKNN rolling algorithm that pads unknown users with user metadata benchmarked using MovieLens dataset.',
    imgSrc: '/dataset-card/movielens.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/examples/movielens_itemknn_incremental_metadatapad.ipynb',
  },
];

const page = () => {
  return (
    <>
      <Title order={1} mb={20}>
        How To Use Streamsight
      </Title>
      <Divider my="md" />
      <Title order={3} mb={20}>
        Sample Notebooks
        <Text fw={700}>
          Learn through example notebooks in Streamsight on how to use Streamsight, and explore the
          array of algorithms we have implemented.
        </Text>
      </Title>
      <Image src="/getting-started/notebooks.jpg" alt="Notebooks" h={200} radius="md" />
      <Text mb={10} mt={20}>
        Interested in contributing?
      </Text>

      <Button
        variant="gradient"
        gradient={{ from: '#1c7ed6', to: '#22b8cf' }}
        radius="xl"
        leftSection={<IconPlus size={14} />}
        component={Link}
        href="https://github.com/suenalaba/streamsightv2/pulls"
      >
        New Notebook
      </Button>
      <Divider my="md" />
      <Group gap="sm" mb={10} mt={20}>
        <IconCode size={30} />
        <Title order={2}>Sample Notebooks</Title>
      </Group>
      <Grid>
        {notebookCards.map((card) => (
          <GridCol span={3} key={card.title}>
            <CardWithTopLogo
              title={card.title}
              description={card.description}
              imgSrc={card.imgSrc}
              imgAlt={card.imgAlt}
              href={card.href}
            />
          </GridCol>
        ))}
      </Grid>
    </>
  );
};

export default page;
