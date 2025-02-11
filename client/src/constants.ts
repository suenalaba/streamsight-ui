import { StreamStatusEnum } from '@/enum';

export const getStatusBadgeProps = (status: StreamStatusEnum) => {
  const StatusToBadgePropsMappings = {
    NOT_STARTED: {
      color: 'gray',
      label: StreamStatusEnum.NOT_STARTED,
    },
    IN_PROGRESS: {
      color: 'blue',
      label: StreamStatusEnum.IN_PROGRESS,
    },
    COMPLETED: {
      color: 'lime',
      label: StreamStatusEnum.COMPLETED,
    },
  };
  return StatusToBadgePropsMappings[status];
};

export const BASE_SERVER_URL = process.env.NEXT_PUBLIC_SERVER_URL || 'http://127.0.0.1:8000';
export const BASE_CLIENT_URL = process.env.NEXT_PUBLIC_CLIENT_URL || 'http://127.0.0.1:3000';
