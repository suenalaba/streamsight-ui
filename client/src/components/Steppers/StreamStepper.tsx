import React, { useEffect, useState } from 'react';
import { Stepper } from '@mantine/core';
import { StreamStatusEnum } from '@/enum';

interface StreamStepperProps {
  status: StreamStatusEnum;
}

const StreamStepper = ({ status }: StreamStepperProps) => {
  const getStepFromStatus = (status: StreamStatusEnum) => {
    switch (status) {
      case StreamStatusEnum.NOT_STARTED:
        return 1;
      case StreamStatusEnum.IN_PROGRESS:
        return 2;
      case StreamStatusEnum.COMPLETED:
        return 3;
      default:
        return 1;
    }
  };

  const [active, setActive] = useState(1);
  useEffect(() => {
    setActive(getStepFromStatus(status));
  }, [status]);

  return (
    <>
      <Stepper active={active}>
        <Stepper.Step label="First step" description="Create Stream">
          Create Stream
        </Stepper.Step>
        <Stepper.Step label="Second step" description="Start Stream">
          Stream Created, Register Your Algorithms above, then start stream.
        </Stepper.Step>
        <Stepper.Step label="Final step" description="Submit Predictions">
          Stream started, start getting training, unlabeled data and submit predictions.
        </Stepper.Step>
        <Stepper.Completed>Stream Completed. View Metrics Below.</Stepper.Completed>
      </Stepper>
    </>
  );
};

export default StreamStepper;
