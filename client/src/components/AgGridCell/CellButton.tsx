import React from 'react';
import { Button } from '@mantine/core';

interface CellButtonProps {
  color: string;
  disabled?: boolean;
  label: string;
  handleClick: () => void;
}

const CellButton = ({ color, disabled, label, handleClick }: CellButtonProps) => {
  return (
    <Button onClick={handleClick} variant="filled" color={color} disabled={disabled}>
      {label}
    </Button>
  );
};

export default CellButton;
