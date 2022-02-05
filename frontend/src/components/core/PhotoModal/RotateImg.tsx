import React from 'react';
import RotateRightIcon from '@material-ui/icons/RotateRight';
import { IconButton } from '@material-ui/core';

export const RotateImg = ({
  turnAngle,
  setTurnAngle,
}: {
  turnAngle: number;
  setTurnAngle: React.Dispatch<React.SetStateAction<number>>;
}): React.ReactElement => {
  const handleRotateImg = (): void => {
    document
      .getElementById('modalImg')
      .setAttribute('style', `transform: rotate(${turnAngle}deg)`);
    setTurnAngle((prev) => prev + 90);
  };

  return (
    <IconButton onClick={() => handleRotateImg()}>
      <RotateRightIcon />
    </IconButton>
  );
};
