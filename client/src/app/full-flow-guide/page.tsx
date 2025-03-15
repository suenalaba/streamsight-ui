import React from 'react';
import {
  IconBrandYoutubeFilled,
  IconDeviceImac,
  IconGitBranch,
  IconGitCommit,
  IconGitPullRequest,
  IconMessageDots,
  IconPlayerPlay,
  IconReportAnalytics,
} from '@tabler/icons-react';
import {
  Anchor,
  Box,
  Code,
  Divider,
  Image,
  Text,
  Timeline,
  TimelineItem,
  Title,
} from '@mantine/core';
import { BASE_CLIENT_URL } from '@/constants';

const codeForConfiguringLocalHost = `from streamsightv2.algorithms import ItemKNNIncremental

external_model = ItemKNNIncremental(K=2)

# Replace with actual stream_id and algorithm_id
stream_id = "cf42abee-c48c-4013-b229-1c6d2f949f80"
algorithm_id = "bdd640fb-0667-4ad1-9c80-317fa3b1799d"
`;

const codeForFittingTrainingData = `import requests

# Define the base URL and endpoint
base_url = "https://streamsight-server.onrender.com"
endpoint = "/streams/{stream_id}/algorithms/{algorithm_id}/training-data"

# Construct the full URL to get training data
url = f"{base_url}{endpoint.format(stream_id=stream_id, algorithm_id=algorithm_id)}"
response = requests.get(url)
training_df = pd.DataFrame(response.json().get('training_data'))
shape = response.json().get('shape')

from streamsightv2.matrix import InteractionMatrix
# construct the interaction matrix
training_im = InteractionMatrix(training_df, item_ix='iid', user_ix='uid', timestamp_ix='ts', shape=shape)

# fit to your model
external_model.fit(training_im)
`;

const codeForPredictingUnlabeledData = `import requests

# Define the base URL and endpoint
base_url = "https://streamsight-server.onrender.com"
endpoint = "/streams/{stream_id}/algorithms/{algorithm_id}/unlabeled-data"

# Construct the full URL to get unlabeled data
url = f"{base_url}{endpoint.format(stream_id=stream_id, algorithm_id=algorithm_id)}"
response = requests.get(url)
ul_df = pd.DataFrame(response.json().get('unlabeled_data'))
shape = response.json().get('shape')

# construct the interaction matrix
ul_im = InteractionMatrix(ul_df, item_ix='iid', user_ix='uid', timestamp_ix='ts', shape=shape)

# predict on your model
prediction = external_model.predict(training_im, ul_im)
`;

const codeForSubmittingPredictions = `# convert your csr_matrix into a matrix_dict
matrix_dict = {
    'data': prediction.data.tolist(),
    'indices': prediction.indices.tolist(),
    'indptr': prediction.indptr.tolist(),
    'shape': prediction.shape
}

import requests

# Define the base URL and endpoint
base_url = "https://streamsight-server.onrender.com"
endpoint = "/streams/{stream_id}/algorithms/{algorithm_id}/predictions"

# Construct the full URL for submitting predictions
url = f"{base_url}{endpoint.format(stream_id=stream_id, algorithm_id=algorithm_id)}"

# submit predictions to streamsight-ui
response = requests.post(url, json=matrix_dict)
`;

const codeForCheckingIfStreamIsCompleted = `import requests

# Define the base URL and endpoint
base_url = "https://streamsight-server.onrender.com"
endpoint = "/streams/{stream_id}/algorithms/{algorithm_id}/is-completed"

# Construct the full URL to check if stream is completed
url = f"{base_url}{endpoint.format(stream_id=stream_id, algorithm_id=algorithm_id)}"
response = requests.get(url)
# prints True if stream is completed, False otherwise
print(response.content)
`;

const codeForViewingMetrics = `import requests

# Define the base URL and endpoint
base_url = "https://streamsight-server.onrender.com"
endpoint = "/streams/{stream_id}/metrics"

# Construct the full URL to get metrics
url = f"{base_url}{endpoint.format(stream_id=stream_id)}"
response = requests.get(url)

response_data = response.json()
# Display Micro Metrics
print("Micro Metrics:")
for metric in response_data["micro_metrics"]:
    print(f"Algorithm: {metric['algorithm_name']} (ID: {metric['algorithm_id']})")
    print(f"  Metric: {metric['metric']}")
    print(f"  Micro Score: {metric['micro_score']}")
    print(f"  Number of Users: {metric['num_user']}\n")

# Display Macro Metrics
print("Macro Metrics:")
for metric in response_data["macro_metrics"]:
    print(f"Algorithm: {metric['algorithm_name']} (ID: {metric['algorithm_id']})")
    print(f"  Metric: {metric['metric']}")
    print(f"  Macro Score: {metric['macro_score']}")
    print(f"  Number of Windows: {metric['num_window']}\n")
`;

const page = () => {
  return (
    <>
      <Title order={1} mb={20}>
        How To Use Streamsight
      </Title>
      <Box style={{ overflowX: 'auto', width: '100%' }}>
        <Image src="/full-stream-flow-guide/full_flow.png" alt="Full User Flow" h={574} w={2895} />
      </Box>
      <Divider my="md" />
      <Title order={3} mb={20}>
        Full User Flow
        <Text fw={700}>Find out how to use Streamsight to its full potential</Text>
      </Title>
      <Divider my="md" />
      <Timeline active={7} bulletSize={24} lineWidth={2}>
        <TimelineItem bullet={<IconGitBranch size={12} />} title="Create Stream">
          <Text c="dimmed" size="sm">
            Configure your settings at:{' '}
            <Anchor
              href={`${BASE_CLIENT_URL}/stream/create`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {`${BASE_CLIENT_URL}/stream/create`}
            </Anchor>
          </Text>
          <Text size="xs" mt={4}>
            Step 1
          </Text>
        </TimelineItem>

        <TimelineItem bullet={<IconGitCommit size={12} />} title="Obtain Stream ID">
          <Text c="dimmed" size="sm">
            Stream ID is unique to each stream and is used to identify your stream
          </Text>
          <Image src="/full-stream-flow-guide/step2.png" alt="Get Stream ID" />
          <Text size="xs" mt={4}>
            Step 2
          </Text>
        </TimelineItem>

        <TimelineItem title="Stream Page" bullet={<IconGitPullRequest size={12} />}>
          <Text c="dimmed" size="sm">
            Check stream settings and register your algorithms at:{' '}
            <Anchor
              href={`${BASE_CLIENT_URL}/stream/{your-stream-id}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {`${BASE_CLIENT_URL}/stream/{your-stream-id}`}
            </Anchor>
          </Text>
          <Text size="xs" mt={4}>
            Step 3
          </Text>
        </TimelineItem>

        <TimelineItem title="Registering Algorithms" bullet={<IconMessageDots size={12} />}>
          <Text c="dimmed" size="sm">
            Register your algorithms that you want to run on your stream with these settings. Giving
            a unique name to your algorithm will help you identify it later.
          </Text>
          <Image src="/full-stream-flow-guide/step4.png" alt="Register Algorithm" />
          <Text size="xs" mt={4}>
            Step 4
          </Text>
        </TimelineItem>

        <TimelineItem
          lineVariant="dashed"
          title="Start Stream"
          bullet={<IconPlayerPlay size={12} />}
        >
          <Text c="dimmed" size="sm">
            Once settings are appropriate and algorithms are registered, start your stream at:{' '}
            <Anchor href={`${BASE_CLIENT_URL}/stream`} target="_blank" rel="noopener noreferrer">
              {`${BASE_CLIENT_URL}/stream`}
            </Anchor>
          </Text>
          <Image src="/full-stream-flow-guide/step5.png" alt="Start Stream" />
          <Text size="xs" mt={4}>
            Step 5
          </Text>
        </TimelineItem>

        <TimelineItem title="Configure LocalHost" bullet={<IconDeviceImac size={12} />}>
          <Text c="dimmed" size="sm">
            Obtain your stream ID and relevant algorithm IDs to configure your localhost.
          </Text>
          <Image src="/full-stream-flow-guide/step6.png" alt="Configure localhost" />
          <Text c="dimmed" size="sm">
            Configure your localhost with the following code. Here, we assume you have already
            implemented your own algorithm. We use our own Streamsight Algorithm as an example, you
            can find out how to implement yours here:
            <Anchor
              href={`${BASE_CLIENT_URL}/create-algorithm-guide`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {`${BASE_CLIENT_URL}/create-algorithm-guide`}
            </Anchor>
          </Text>
          <Code color="var(--mantine-color-blue-light)" block>
            {codeForConfiguringLocalHost}
          </Code>
          <Text size="xs" mt={4}>
            Step 6
          </Text>
        </TimelineItem>

        <TimelineItem bullet={<IconBrandYoutubeFilled size={12} />} title="Streaming Process">
          <Text c="dimmed" size="sm">
            After configuring your localhost, you are now ready to start the data exchange process.
            Repeat the following steps for each iteration until the stream is completed.
          </Text>
          <Text size="sm">Each iteration consists of 4 steps:</Text>
          <Text size="sm">1. Fit the training data.</Text>
          <Code color="var(--mantine-color-blue-light)" block>
            {codeForFittingTrainingData}
          </Code>
          <Text size="sm">2. Predict on unlabeled data.</Text>
          <Code color="var(--mantine-color-blue-light)" block>
            {codeForPredictingUnlabeledData}
          </Code>
          <Text size="sm">3. Submit Predictions.</Text>
          <Code color="var(--mantine-color-blue-light)" block>
            {codeForSubmittingPredictions}
          </Code>
          <Text size="sm">4. Check if stream is completed.</Text>
          <Code color="var(--mantine-color-blue-light)" block>
            {codeForCheckingIfStreamIsCompleted}
          </Code>
          <Text size="xs" mt={4}>
            Step 8
          </Text>
        </TimelineItem>

        <TimelineItem
          title="Obtainining RecSys Evaluation Metrics"
          bullet={<IconReportAnalytics size={12} />}
        >
          <Text c="dimmed" size="sm">
            Obtain your stream ID and relevant algorithm IDs to configure your localhost.
          </Text>
          <Text c="dimmed" size="sm">
            Once the stream is completed you can view your metrics on our dashboard at:{' '}
            <Anchor
              href={`${BASE_CLIENT_URL}/stream/{your-stream-id}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {`${BASE_CLIENT_URL}/stream/{your-stream-id}`}
            </Anchor>{' '}
            or you can view the metrics on your localhost with
          </Text>
          <Code color="var(--mantine-color-blue-light)" block>
            {codeForViewingMetrics}
          </Code>
          <Text size="xs" mt={4}>
            Step 9
          </Text>
        </TimelineItem>
      </Timeline>
    </>
  );
};

export default page;
