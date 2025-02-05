import Link from 'next/link';
import {
  IconArrowRight,
  IconCode,
  IconDatabase,
  IconFileDatabase,
  IconHierarchy,
  IconNumber10Small,
  IconPercentage30,
  IconSitemap,
} from '@tabler/icons-react';
import { Button, Flex, Grid, Group, Image, Text, Title } from '@mantine/core';
import WelcomePageCard from '../WelcomePageCard/WelcomePageCard';
import classes from './Welcome.module.css';

const introductionText =
  'Join the Streamsight community which provides a new perspective of evaluating your RecSys algorithm which respects the temporal ordering of interactions on a global timeline. Conduct your research in a way that mimics an online setting as closely as possible.';

const datasetCards = [
  {
    title: 'Amazon Music Data',
    description: 'Contains metadata and reviews of Amazon Music products.',
    imgSrc: '/dataset-card/amazon.png',
    imgAlt: 'Amazon logo',
    href: 'https://amazon-reviews-2023.github.io/',
    icon: null,
  },
  {
    title: 'LastFM Dataset',
    description: 'Contains metadata and reviews of LastFM dataset.',
    imgSrc: '/dataset-card/lastfm.png',
    imgAlt: 'LastFM logo',
    href: 'https://files.grouplens.org/datasets/hetrec2011/hetrec2011-lastfm-readme.txt',
    icon: null,
  },
  {
    title: 'MovieLens Dataset',
    description: 'Contains metadata and reviews of Movielens.',
    imgSrc: '/dataset-card/movielens.png',
    imgAlt: 'MovieLens logo',
    href: 'https://grouplens.org/datasets/movielens/100k/',
    icon: null,
  },
  {
    title: 'Yelp Dataset',
    description: 'Contains metadata and reviews of Yelp user reviews.',
    imgSrc: '/dataset-card/yelp.png',
    imgAlt: 'Yelp logo',
    href: 'https://business.yelp.com/data/resources/open-dataset/',
    icon: null,
  },
];

const notebookCards = [
  {
    title: 'RecentPop Algorithm with MovieLens Dataset',
    description:
      'Demonstration of the RecentPop algorithm baseline using the MovieLens dataset. This offers a different perspective of the Popularity baseline.',
    imgSrc:
      'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-5.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/examples/movielens_recentpop.ipynb',
    icon: null,
  },
  {
    title: 'DecayPop Algorithm with MovieLens Dataset',
    description:
      'Demonstration of the DecayPop algorithm baseline using the MovieLens dataset. This offers a different perspective of the Popularity baseline.',
    imgSrc:
      'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-2.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/examples/movielens_decaypop.ipynb',
    icon: null,
  },
  {
    title: 'ItemKNN Incremental (RecentPop Padding) with MovieLens Dataset',
    description:
      'ItemKNN incremental algorithm that pads unknown users with RecentPop Algorithm benchmarked with the MovieLens dataset.',
    imgSrc:
      'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-4.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/examples/movielens_itemknn_incremental_randompad.ipynb',
    icon: null,
  },
  {
    title: 'ItemKNN Incremental (Metadata Padding) with MovieLens Dataset',
    description:
      'A demonstration of the ItemKNN rolling algorithm that pads unknown users with user metadata benchmarked using MovieLens dataset.',
    imgSrc:
      'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-9.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/examples/movielens_itemknn_incremental_metadatapad.ipynb',
    icon: null,
  },
];

const modelCards = [
  {
    title: 'RecentPop',
    description: 'Demonstration of the RecentPop algorithm baseline.',
    imgSrc:
      'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-5.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/streamsight/algorithms/baseline.py',
    icon: <IconPercentage30 size={20} />,
  },
  {
    title: 'DecayPop',
    description: 'Demonstration of the DecayPop algorithm baseline.',
    imgSrc:
      'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-2.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/streamsight/algorithms/baseline.py',
    icon: <IconNumber10Small size={20} />,
  },
  {
    title: 'ItemKNN Incremental (RecentPop Padding)',
    description: 'ItemKNN incremental algorithm that pads unknown users with RecentPop Algorithm.',
    imgSrc:
      'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-4.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/streamsight/algorithms/itemknn_incremental.py',
    icon: <IconSitemap size={20} />,
  },
  {
    title: 'ItemKNN Incremental (Metadata Padding)',
    description: 'ItemKNN incremental algorithm that pads unknown users with metadata.',
    imgSrc:
      'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-9.png',
    imgAlt: 'Avatar',
    href: 'https://github.com/suenalaba/streamsightv2/blob/master/streamsight/algorithms/itemknn_incremental.py',
    icon: <IconFileDatabase size={20} />,
  },
];

export function Welcome() {
  return (
    <>
      <Image src="/streamsight-logo.png" alt="Streamsight" />

      <Flex align="flex-start" wrap="wrap" gap="md">
        <Flex direction="column" style={{ flex: 1, minWidth: 0 }}>
          <Title className={classes.title} mt={20}>
            Level up with{' '}
            <Text
              inherit
              variant="gradient"
              component="span"
              gradient={{ from: 'pink', to: 'yellow' }}
            >
              Streamsight,
            </Text>
          </Title>
          <Title className={classes.title}>a fresh way to evaluate your RecSys algorithm.</Title>
          <Text size="md" maw={580} mt={10}>
            {introductionText}
          </Text>
        </Flex>
      </Flex>

      <Title order={2} mb={30} mt={50}>
        Who's on Streamsight?
      </Title>
      <Grid>
        <Grid.Col span={4}>
          <Flex align="flex-start" wrap="wrap" gap="md">
            <Flex direction="column" style={{ flex: 1, minWidth: 0 }}>
              <Title order={3}>Students</Title>
              <Text>
                Leverage examples and use Streamsight notebooks to learn more about state-of-the-art
                RecSys.
              </Text>
            </Flex>

            <Image src="/welcome/student.png" alt="Students" h={100} w={100} />
          </Flex>
        </Grid.Col>

        <Grid.Col span={4}>
          <Flex align="flex-start" wrap="wrap" gap="md">
            <Flex direction="column" style={{ flex: 1, minWidth: 0 }}>
              <Title order={3}>Developers</Title>
              <Text>
                Create your own algorithms with Streamsight's modular design & datasets to evaluate
                your RecSys algorithm against our evaluation platform.
              </Text>
            </Flex>

            <Image src="/welcome/developer.png" alt="Learners" h={100} w={100} />
          </Flex>
        </Grid.Col>

        <Grid.Col span={4}>
          <Flex align="flex-start" wrap="wrap" gap="md">
            <Flex direction="column" style={{ flex: 1, minWidth: 0 }}>
              <Title order={3}>Researchers</Title>
              <Text>
                Advance the way we evaluate RecSys algorithm with respect for temporal ordering of
                interactions.
              </Text>
            </Flex>

            <Image src="/welcome/researcher.png" alt="Researchers" h={100} w={100} />
          </Flex>
        </Grid.Col>
      </Grid>

      {/* Datasets */}
      <Group justify="space-between" align="center" mt={50}>
        <Group gap="sm" mb={10}>
          <IconDatabase size={30} />
          <Title order={2}>Datasets</Title>
        </Group>

        <Button
          component={Link}
          href="https://github.com/suenalaba/streamsightv2/tree/master/streamsight/datasets"
          variant="subtle"
          color="black"
          radius="xl"
          leftSection={<IconArrowRight />}
        >
          View All
        </Button>
      </Group>
      <Text mb={20}>
        7++ high-quality and publicly available RecSys datasets including those listed on ACM.
        Everything from music to movies.
      </Text>
      <Grid>
        {datasetCards.map((card) => (
          <Grid.Col span={3} key={card.title}>
            <WelcomePageCard
              title={card.title}
              description={card.description}
              imgSrc={card.imgSrc}
              imgAlt={card.imgAlt}
              href={card.href}
            />
          </Grid.Col>
        ))}
      </Grid>

      {/* Notebooks */}
      <Group justify="space-between" align="center" mt={50}>
        <Group gap="sm" mb={10}>
          <IconCode size={30} />
          <Title order={2}>Notebooks</Title>
        </Group>

        <Button
          component={Link}
          href="https://github.com/suenalaba/streamsightv2/tree/master/examples"
          variant="subtle"
          color="black"
          radius="xl"
          leftSection={<IconArrowRight />}
        >
          View All
        </Button>
      </Group>
      <Text mb={20}>
        10++ publicly available Notebooks on Streamsight for you to reference and to learn from.
      </Text>
      <Grid>
        {notebookCards.map((card) => (
          <Grid.Col span={3} key={card.title}>
            <WelcomePageCard
              displayAsAvatar
              title={card.title}
              description={card.description}
              imgSrc={card.imgSrc}
              imgAlt={card.imgAlt}
              href={card.href}
            />
          </Grid.Col>
        ))}
      </Grid>

      {/* Models */}
      <Group justify="space-between" align="center" mt={50}>
        <Group gap="sm" mb={10}>
          <IconHierarchy size={30} />
          <Title order={2}>Models</Title>
        </Group>

        <Button
          component={Link}
          href="https://github.com/suenalaba/streamsightv2/tree/master/streamsight/algorithms"
          variant="subtle"
          color="black"
          radius="xl"
          leftSection={<IconArrowRight />}
        >
          View All
        </Button>
      </Group>
      <Text mb={20}>
        Reinvented baseline algorithms suited for Streamsight's evaluation platform. And baseline
        models with different padding strategies.
      </Text>
      <Grid>
        {modelCards.map((card) => (
          <Grid.Col span={3} key={card.title}>
            <WelcomePageCard
              displayAsAvatar
              title={card.title}
              description={card.description}
              imgSrc={card.imgSrc}
              imgAlt={card.imgAlt}
              href={card.href}
              icon={card.icon}
            />
          </Grid.Col>
        ))}
      </Grid>
    </>
  );
}
