import React from 'react';
import { Button } from '@mantine/core';

interface CellButtonProps {
  color: string;
  disabled?: boolean;
  label: string;
}

const CellButton = ({ color, disabled, label }: CellButtonProps) => {
  return (
    <Button variant="filled" color={color} disabled={disabled}>
      {label}
    </Button>
  );
};

export default CellButton;
