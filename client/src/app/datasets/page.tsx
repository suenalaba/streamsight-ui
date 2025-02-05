import React from 'react';
import Link from 'next/link';
import { IconPlus, IconTrendingUp } from '@tabler/icons-react';
import { Button, Divider, Flex, Grid, GridCol, Group, Image, Text, Title } from '@mantine/core';
import DatasetPageCard from '@/components/Cards/DatasetPageCard';

const datasetDescription =
  'Explore and analyze a wide array of datasets available on Streamsight. Some of these datasets are recommended by ACM for RecSys conference. Most are popular benchmarks used in RecSys evaluation and benchmarking.';

const datasetCards = [
  {
    title: 'Amazon Music Data',
    description: 'Contains metadata and reviews of Amazon Music products.',
    imgSrc: '/dataset-card/amazon.png',
    imgAlt: 'Amazon logo',
    href: 'https://amazon-reviews-2023.github.io/',
  },
  {
    title: 'LastFM Dataset',
    description: 'Contains metadata and reviews of LastFM dataset.',
    imgSrc: '/dataset-card/lastfm.png',
    imgAlt: 'LastFM logo',
    href: 'https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-readme.txt',
  },
  {
    title: 'MovieLens Dataset',
    description: 'Contains metadata and reviews of Movielens.',
    imgSrc: '/dataset-card/movielens.png',
    imgAlt: 'MovieLens logo',
    href: 'https://grouplens.org/datasets/movielens/100k/',
  },
  {
    title: 'Yelp Dataset',
    description: 'Contains metadata and reviews of Yelp user reviews.',
    imgSrc: '/dataset-card/yelp.png',
    imgAlt: 'Yelp logo',
    href: 'https://business.yelp.com/data/resources/open-dataset/',
  },
  {
    title: 'Amazon Movie Data',
    description: 'Contains metadata and reviews of Amazon Movies.',
    imgSrc: '/dataset-card/amazon.png',
    imgAlt: 'Amazon logo',
    href: 'https://amazon-reviews-2023.github.io/',
  },
  {
    title: 'Amazon Subscription Data',
    description: 'Contains metadata and reviews of Amazon Subscription Boxes.',
    imgSrc: '/dataset-card/amazon.png',
    imgAlt: 'Amazon logo',
    href: 'https://amazon-reviews-2023.github.io/',
  },
  {
    title: 'Amazon Book Data',
    description: 'Contains metadata and reviews of Amazon Books.',
    imgSrc: '/dataset-card/amazon.png',
    imgAlt: 'Amazon logo',
    href: 'https://amazon-reviews-2023.github.io/',
  },
];

const page = () => {
  return (
    <>
      <Flex align="flex-start" wrap="wrap" gap="md">
        <Flex direction="column" style={{ flex: 1, minWidth: 0 }}>
          <Grid>
            <GridCol span={6}>
              <Title mb={30}>Datasets</Title>
              <Text mb={60}>{datasetDescription}</Text>
              <Text mb={10}>Don't see a dataset you want?</Text>

              <Button
                variant="gradient"
                gradient={{ from: '#1c7ed6', to: '#22b8cf' }}
                radius="xl"
                leftSection={<IconPlus size={14} />}
                component={Link}
                href="https://github.com/suenalaba/streamsightv2/issues"
              >
                New Dataset
              </Button>
            </GridCol>
            <GridCol span={6}>
              <Flex justify="flex-end">
                <Image src="/datasets-logo.avif" alt="Datasets-Logo" h={280} w={280} />
              </Flex>
            </GridCol>
          </Grid>
        </Flex>
      </Flex>
      <Divider my="md" />
      <Group gap="sm" mb={10} mt={20}>
        <IconTrendingUp size={30} />
        <Title order={2}>RecSys Datasets</Title>
      </Group>
      <Grid>
        {datasetCards.map((card) => (
          <GridCol span={3} key={card.title}>
            <DatasetPageCard
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
