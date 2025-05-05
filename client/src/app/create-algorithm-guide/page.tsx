import React from 'react';
import { Anchor, Code, Divider, Image, Text, Title } from '@mantine/core';

const codeForOwnAlgorithmBoilerPlate = `# all algorithms should inherit from the Algorithm class
from streamsightv2.algorithms.base import Algorithm

class YourOwnAlgorithm(Algorithm):
    """Create your own algorithm

    Only the _fit and _predict methods need to be implemented.
    """

    def __init__(self, K=10):
        super().__init__(K=K)

    def _fit(self, X: csr_matrix) -> "YourOwnAlgorithm":
        """You should implement the fit method here."""
        
    def _predict(self, X: csr_matrix, predict_im: InteractionMatrix) -> csr_matrix:
        """You should implement the _predict method here and return a csr_matrix with the predictions."""
`;

const page = () => {
  return (
    <>
      <Title order={1} mb={20}>
        How To Use Streamsight
      </Title>
      <Divider my="md" />
      <Title order={3} mb={20}>
        Create Your Own Algorithm
        <Text fw={700}>
          Find out how to create your own RecSys algorithm and integrate it with Streamsight to
          evaluate your algorithms.
        </Text>
      </Title>
      <Image
        src="/getting-started/create-own-algorithm.jpg"
        alt="Create Your Own Algorithm"
        h={200}
        radius="md"
      />
      <Divider my="md" />
      <Text size="sm">
        You can copy this boilerplate code and create your own algorithm in Streamsight. Only the{' '}
        <Code color="blue.9" c="white">
          _fit
        </Code>{' '}
        and{' '}
        <Code color="blue.9" c="white">
          _predict
        </Code>{' '}
        methods need to be implemented. However, you can also implement other methods if needed.
      </Text>
      <Code color="var(--mantine-color-blue-light)" block>
        {codeForOwnAlgorithmBoilerPlate}
      </Code>
      <Text size="sm">
        If you need some inspiration, you can check out the algorithms that are already implemented
        in Streamsight. You can find them here:{' '}
        <Anchor
          href="https://github.com/suenalaba/streamsightv2/tree/master/streamsightv2/algorithms"
          target="_blank"
          rel="noopener noreferrer"
        >
          https://github.com/suenalaba/streamsightv2/tree/master/streamsightv2/algorithms
        </Anchor>
      </Text>
    </>
  );
};

export default page;
